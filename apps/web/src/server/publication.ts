import 'server-only';
import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import registry from '../../../../content/publication.json';
import { buildEnv, type AppEnv } from './config';

export type RouteStatus = 'draft' | 'review' | 'approved' | 'published' | 'archived';
export type PublicRoute = {
  id: string;
  path: string;
  family: string;
  title: string;
  description: string;
  jsonLd: unknown;
  status: RouteStatus;
  environments: string[];
  approval: string | null;
};

const routes = registry.routes as PublicRoute[];
// `next build` runs in apps/web; the standalone release runs from the package root.
// Content is traced into the release by outputFileTracingIncludes in next.config.ts.
const contentDir = [path.join(/*turbopackIgnore: true*/ process.cwd(), '..', '..', 'content'), path.join(/*turbopackIgnore: true*/ process.cwd(), 'content')]
  .find(dir => existsSync(path.join(dir, 'publication.json'))) ?? path.join(/*turbopackIgnore: true*/ process.cwd(), 'content');

/**
 * Production serves only owner-approved, published routes. Local and dev also show pages in review.
 * Anything else fails closed with a 404.
 */
export function isPublic(route: PublicRoute, env: AppEnv = buildEnv): boolean {
  if (!route.environments.includes(env)) return false;
  if (env === 'production') return route.status === 'published' && Boolean(route.approval);
  return route.status === 'review' || route.status === 'approved' || route.status === 'published';
}

export function publicRoutes(env: AppEnv = buildEnv): PublicRoute[] {
  return routes.filter(route => isPublic(route, env));
}

export function findRoute(id: string): PublicRoute | undefined {
  return routes.find(route => route.id === id);
}

export function readFragment(...parts: string[]): string {
  return readFileSync(path.join(contentDir, ...parts), 'utf8');
}
