export type AppEnv = 'local' | 'development' | 'production';

/** Canonical, social and schema URLs always use the apex production origin. */
export const CANONICAL_ORIGIN = 'https://usjunkcars.si';

const ORIGINS: Record<AppEnv, string | null> = {
  local: null,
  development: 'https://dev.usjunkcars.si',
  production: 'https://usjunkcars.si',
};

function parseEnv(value: string | undefined): AppEnv {
  const env = value ?? 'local';
  if (env !== 'local' && env !== 'development' && env !== 'production') {
    throw new Error(`Unsupported APP_ENV "${env}"`);
  }
  return env;
}

/** The environment this build was produced for (inlined at build time). */
export const buildEnv: AppEnv = parseEnv(process.env.BUILD_APP_ENV);

/** Refuse to serve a build under a different environment or origin than it was built for. */
export function assertRuntimeMatchesBuild(): void {
  const runtime = parseEnv(process.env.APP_ENV);
  if (runtime !== buildEnv) {
    throw new Error(`Build for ${buildEnv} cannot run as ${runtime}`);
  }
  const expected = ORIGINS[runtime];
  const site = process.env.SITE_URL;
  if (expected && site && site !== expected) {
    throw new Error(`SITE_URL ${site} does not match ${runtime} origin ${expected}`);
  }
}
