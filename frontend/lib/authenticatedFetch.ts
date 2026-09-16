import {
  auth,
} from "./firebase";


export async function authenticatedFetch(
  input: Parameters<typeof fetch>[0],
  init: Parameters<typeof fetch>[1] = {},
) {
  const user =
    auth.currentUser;


  if (!user) {
    throw new Error(
      "Authentication required."
    );
  }


  const token =
    await user.getIdToken();


  const headers =
    new Headers(
      init?.headers
    );


  headers.set(
    "Authorization",
    `Bearer ${token}`
  );


  return fetch(
    input,
    {
      ...init,
      headers,
    }
  );
}
