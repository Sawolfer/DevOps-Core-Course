export interface Env {
  APP_NAME: string;
  COURSE_NAME: string;
  API_TOKEN: string;
  ADMIN_EMAIL: string;
  SETTINGS: KVNamespace;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const cf = request.cf as IncomingRequestCfProperties | undefined;

    console.log(
      JSON.stringify({
        path: url.pathname,
        method: request.method,
        colo: cf?.colo ?? "unknown",
        country: cf?.country ?? "unknown",
        userAgent: request.headers.get("user-agent") ?? "unknown",
      })
    );

    try {
      if (url.pathname === "/health") {
        return Response.json({
          status: "healthy",
          app: env.APP_NAME,
          timestamp: new Date().toISOString(),
        });
      }

      if (url.pathname === "/") {
        return Response.json({
          app: env.APP_NAME,
          course: env.COURSE_NAME,
          description: "Lab 17 - Cloudflare Workers Edge API",
          version: "1.0.0",
          endpoints: [
            { path: "/", method: "GET", description: "Service information" },
            { path: "/health", method: "GET", description: "Health check" },
            { path: "/edge", method: "GET", description: "Edge metadata" },
            { path: "/counter", method: "GET", description: "KV-backed counter" },
          ],
          timestamp: new Date().toISOString(),
        });
      }

      if (url.pathname === "/edge") {
        const metadata = {
          colo: cf?.colo ?? "unknown",
          country: cf?.country ?? "unknown",
          city: cf?.city ?? "unknown",
          asn: cf?.asn ?? 0,
          httpProtocol: cf?.httpProtocol ?? "unknown",
          tlsVersion: cf?.tlsVersion ?? "unknown",
          timezone: cf?.timezone ?? "unknown",
          continent: cf?.continent ?? "unknown",
          clientAcceptEncoding: cf?.clientAcceptEncoding ?? "unknown",
          asOrganization: cf?.asOrganization ?? "unknown",
        };

        return Response.json({
          endpoint: "/edge",
          metadata,
          message: "Request processed at Cloudflare edge",
          app_id: env.APP_NAME,
        });
      }

      if (url.pathname === "/counter") {
        const raw = await env.SETTINGS.get("visits");
        const visits = Number(raw ?? "0") + 1;
        await env.SETTINGS.put("visits", String(visits));

        return Response.json({
          endpoint: "/counter",
          visits,
          admin: env.ADMIN_EMAIL ? env.ADMIN_EMAIL.replace(/(?<=.).(?=[^@]*?.@)/g, "*") : "not set",
          storage: "Workers KV :: SETTINGS namespace",
        });
      }

      if (url.pathname === "/config") {
        return Response.json({
          app_name: env.APP_NAME,
          course_name: env.COURSE_NAME,
          has_api_token: env.API_TOKEN ? "configured" : "not set",
          has_admin_email: env.ADMIN_EMAIL ? "configured" : "not set",
        });
      }

      return new Response(
        JSON.stringify({
          error: "Not Found",
          message: `Unknown endpoint: ${url.pathname}`,
          available_routes: ["/", "/health", "/edge", "/counter", "/config"],
        }),
        {
          status: 404,
          headers: { "Content-Type": "application/json" },
        }
      );
    } catch (err) {
      console.error("Worker error:", err);
      return new Response(
        JSON.stringify({
          error: "Internal Server Error",
          message: "Something went wrong",
        }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
  },
};
