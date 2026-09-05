/**
 * AppShell — 页面外框
 * SPEC §31 — Header + Main
 */

import type { ReactNode } from 'react';
import { Header } from './Header';

interface Props {
  children: ReactNode;
}

export function AppShell({ children }: Props) {
  return (
    <div className="min-h-100dvh flex flex-col">
      <Header />
      <main className="flex-1 flex flex-col">{children}</main>
    </div>
  );
}
