type LogLevel = "debug" | "info" | "warn" | "error";

const LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
};

/** Client-side structured logger. Never throws; degrades to no-ops when
 * logging is disabled. */
class Logger {
  private readonly enabled: boolean;
  private readonly minLevel: LogLevel;

  constructor() {
    this.enabled =
      process.env.NODE_ENV === "production"
        ? (process.env.NEXT_PUBLIC_LOGGING_ENABLED ?? "false") === "true"
        : true;
    this.minLevel =
      (process.env.NEXT_PUBLIC_LOG_LEVEL as LogLevel | undefined) ?? "info";
  }

  private canLog(level: LogLevel) {
    return this.enabled && LEVEL_ORDER[level] >= LEVEL_ORDER[this.minLevel];
  }

  debug(...args: unknown[]) {
    if (this.canLog("debug")) console.debug("[CrimeKit]", ...args);
  }

  info(...args: unknown[]) {
    if (this.canLog("info")) console.info("[CrimeKit]", ...args);
  }

  warn(...args: unknown[]) {
    if (this.canLog("warn")) console.warn("[CrimeKit]", ...args);
  }

  error(...args: unknown[]) {
    if (this.canLog("error")) console.error("[CrimeKit]", ...args);
  }
}

export const logger = new Logger();
