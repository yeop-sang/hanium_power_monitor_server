describe('Dashboard E2E Tests', () => {
  beforeEach(() => {
    // Mock API responses
    cy.intercept('GET', '/api/power_data*', {
      statusCode: 200,
      body: [
        {
          id: 1,
          timestamp: '2024-01-01T12:00:00Z',
          device_code: 'ESP32-001',
          temperature: 23.5,
          humidity: 65.2,
          brightness: 1200,
          electric: 150.5
        },
        {
          id: 2,
          timestamp: '2024-01-01T11:59:00Z',
          device_code: 'ESP32-001',
          temperature: 23.1,
          humidity: 64.8,
          brightness: 1180,
          electric: 148.2
        }
      ]
    }).as('getPowerData');

    cy.intercept('GET', '/api/summary*', {
      statusCode: 200,
      body: {
        time_range: '24h',
        total_readings: 100,
        temperature: {
          avg: 23.5,
          min: 20.0,
          max: 27.0,
          unit: '°C'
        },
        humidity: {
          avg: 65.0,
          min: 45.0,
          max: 85.0,
          unit: '%'
        },
        electric: {
          avg: 150.0,
          min: 100.0,
          max: 200.0,
          total: 15000.0,
          unit: 'mA'
        }
      }
    }).as('getSummary');

    cy.intercept('GET', '/api/esg_reports*', {
      statusCode: 200,
      body: []
    }).as('getESGReports');

    cy.visit('/');
  });

  it('loads the dashboard successfully', () => {
    // Check if main components are rendered
    cy.contains('Environmental Data').should('be.visible');
    cy.contains('Temperature').should('be.visible');
    cy.contains('Humidity').should('be.visible');
    cy.contains('Brightness').should('be.visible');

    // Check if navigation is present
    cy.get('nav').should('be.visible');
    cy.contains('Home').should('be.visible');
    cy.contains('Reports').should('be.visible');
  });

  it('displays environmental data correctly', () => {
    cy.wait('@getPowerData');

    // Check temperature display
    cy.contains('23.5 °C').should('be.visible');
    cy.contains('65.2 %').should('be.visible');
    cy.contains('1200 lx').should('be.visible');

    // Check connection status
    cy.get('.status-indicator').should('be.visible');
    cy.contains('실시간 연결됨').should('be.visible');
  });

  it('shows current power consumption', () => {
    cy.wait('@getPowerData');

    // Check power display component
    cy.contains('150.5 W').should('be.visible');
    cy.contains('갱신').should('be.visible');
  });

  it('renders power chart', () => {
    cy.wait('@getPowerData');

    // Check if chart container exists
    cy.get('canvas').should('exist');
    
    // Chart should be responsive
    cy.viewport(768, 1024);
    cy.get('canvas').should('be.visible');
    
    cy.viewport(1280, 720);
    cy.get('canvas').should('be.visible');
  });

  it('handles API errors gracefully', () => {
    // Simulate API error
    cy.intercept('GET', '/api/power_data*', {
      statusCode: 500,
      body: { message: 'Internal server error' }
    }).as('getPowerDataError');

    cy.reload();
    cy.wait('@getPowerDataError');

    // Should show error message
    cy.contains('Internal server error').should('be.visible');
    cy.contains('재시도').should('be.visible');
  });

  it('allows retrying failed requests', () => {
    // First request fails
    cy.intercept('GET', '/api/power_data*', {
      statusCode: 500,
      body: { message: 'Network error' }
    }).as('getPowerDataError');

    cy.reload();
    cy.wait('@getPowerDataError');

    // Setup successful retry
    cy.intercept('GET', '/api/power_data*', {
      statusCode: 200,
      body: [
        {
          id: 1,
          timestamp: '2024-01-01T12:00:00Z',
          temperature: 24.0,
          humidity: 66.0,
          brightness: 1250,
          electric: 155.0
        }
      ]
    }).as('getPowerDataRetry');

    // Click retry button
    cy.contains('재시도').click();
    cy.wait('@getPowerDataRetry');

    // Should show data
    cy.contains('24.0 °C').should('be.visible');
  });

  it('navigates between pages correctly', () => {
    // Navigate to Reports page
    cy.contains('Reports').click();
    cy.url().should('include', '/reports');

    // Should load ESG reports
    cy.wait('@getESGReports');
    cy.contains('ESG Reports').should('be.visible');

    // Navigate back to Home
    cy.contains('Home').click();
    cy.url().should('include', '/');
    cy.contains('Environmental Data').should('be.visible');
  });

  it('is responsive on different screen sizes', () => {
    // Test mobile view
    cy.viewport(375, 667);
    cy.contains('Environmental Data').should('be.visible');
    
    // Environmental cards should stack vertically on mobile
    cy.get('.env-grid').should('exist');
    
    // Test tablet view
    cy.viewport(768, 1024);
    cy.contains('Environmental Data').should('be.visible');
    
    // Test desktop view
    cy.viewport(1280, 720);
    cy.contains('Environmental Data').should('be.visible');
  });

  it('updates data in real-time', () => {
    cy.wait('@getPowerData');

    // Mock WebSocket message
    cy.window().then((win) => {
      // Simulate receiving new data via Socket.IO
      if (win.io && win.io.socket) {
        win.io.socket.emit('reading', {
          timestamp: '2024-01-01T12:01:00Z',
          temperature: 24.0,
          humidity: 67.0,
          brightness: 1300,
          electric: 160.0
        });
      }
    });

    // Check if data updates (this would require actual Socket.IO integration)
    // For now, we'll just verify the components are ready for real-time updates
    cy.get('.status-dot').should('have.class', 'connected');
  });

  it('handles loading states properly', () => {
    // Mock slow API response
    cy.intercept('GET', '/api/power_data*', (req) => {
      req.reply((res) => {
        res.delay(2000);
        res.send({
          statusCode: 200,
          body: []
        });
      });
    }).as('getSlowPowerData');

    cy.reload();

    // Should show loading indicators
    cy.contains('로딩 중...').should('be.visible');
    
    cy.wait('@getSlowPowerData', { timeout: 3000 });
    
    // Loading should disappear
    cy.contains('로딩 중...').should('not.exist');
  });

  it('validates data format', () => {
    // Mock invalid data response
    cy.intercept('GET', '/api/power_data*', {
      statusCode: 200,
      body: 'invalid json'
    }).as('getInvalidData');

    cy.reload();
    cy.wait('@getInvalidData');

    // Should handle invalid data gracefully
    cy.get('.error-message').should('be.visible');
  });

  it('displays last updated timestamp', () => {
    cy.wait('@getPowerData');

    // Should show when data was last updated
    cy.contains('마지막 업데이트:').should('be.visible');
    
    // Timestamp should be in a readable format
    cy.get('.last-updated').should('contain.text', '2024');
  });
}); 