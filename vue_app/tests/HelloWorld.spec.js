import { render, screen } from '@testing-library/vue';
import HelloWorld from '../src/components/HelloWorld.vue';
import { describe, it, expect } from 'vitest';

describe('HelloWorld Component', () => {
  it('renders props.msg when passed', () => {
    const msg = 'Power Flow';
    render(HelloWorld, { props: { msg } });
    expect(screen.getByText(msg)).toBeInTheDocument();
  });
}); 