export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    const { assertRuntimeMatchesBuild } = await import('./server/config');
    try {
      assertRuntimeMatchesBuild();
    } catch (error) {
      // Exit so the release receiver's health check fails and the previous release stays live.
      console.error(`Refusing to start: ${(error as Error).message}`);
      process.exit(1);
    }
  }
}
