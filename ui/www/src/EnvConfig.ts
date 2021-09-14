export { }

// Declare extensions to custom env vars
declare global {

  interface Env {
    REACT_APP_API_HOST: string,
  }

  interface Window {
     _env_ : Env
  }
}