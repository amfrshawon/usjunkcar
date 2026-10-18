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

/**
 * Peddle instant-offer embed. Production uses the live publisher account; local and dev use the
 * staging account so test submissions never create real offers.
 */
export const PEDDLE = buildEnv === 'production'
  ? { publisherID: '5173226', host: 'https://publisher-embed.peddle.com' }
  : { publisherID: '329729', host: 'https://staging-publisher-embed.peddle.com' };

/**
 * Google Tag Manager loads in every environment so tags can be tested in GTM Preview, but the GA4
 * and Clarity tags inside the container only fire on the production hostname.
 */
export const GTM_ID = 'GTM-TNC9P49R';

export function gtmBootstrap(): string {
  return `window.dataLayer=window.dataLayer||[];window.dataLayer.push({app_env:${JSON.stringify(buildEnv)}});(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer',${JSON.stringify(GTM_ID)});`;
}

/** Peddle's bootstrap snippet (from the publisher dashboard), parameterised by environment. */
export function peddleBootstrap(): string {
  const { publisherID, host } = PEDDLE;
  return `PeddlePublisherEmbedConfig={publisherID:${JSON.stringify(publisherID)},target:null,zIndex:10000},function(){if("function"!=typeof window.PeddlePublisherEmbed){if(!window.PeddlePublisherEmbedConfig||!window.PeddlePublisherEmbedConfig.publisherID)throw new Error("Unable to bootstrap Peddle Publisher Embed, make sure to set PeddlePublisherEmbedConfig.publisherID");const e=(d,i)=>{e.queue.push({operation:d,options:i})};e.queue=[],window.PeddlePublisherEmbed=e;const d=()=>{const e=document.createElement("script");e.type="text/javascript",e.async=!0,e.src=${JSON.stringify(host + '/api/v1/embed/')}+window.PeddlePublisherEmbedConfig.publisherID;const d=document.getElementsByTagName("script")[0];d.parentNode.insertBefore(e,d)};"complete"===document.readyState?d():window.addEventListener("load",d,!1)}}();`;
}
