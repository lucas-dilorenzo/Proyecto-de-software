import { InjectionKey, Ref } from 'vue'

/**
 * Injection key for auth token provider.
 *
 * The value provided by this key is a tuple of:
 *
 * + A ref of the current session token (if any).
 * + A function that can be called to modify the token.
 */
export const authTokenKey: InjectionKey<{
  authToken: Ref<string | undefined>
  setAuthToken(token: string): void
}> = Symbol('AuthTokenKey')
