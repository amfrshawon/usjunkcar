export const dynamic = 'force-dynamic';

/** Release health contract used by the VPS receiver: commit and environment of the running build. */
export function GET() {
  return Response.json(
    { data: { status: 'ok', commit: process.env.RELEASE_SHA ?? null, environment: process.env.APP_ENV ?? 'local' } },
    { headers: { 'Cache-Control': 'no-store' } },
  );
}
