"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";

import {
  FirebaseError,
} from "firebase/app";

import {
  useRouter,
} from "next/navigation";

import {
  auth,
} from "../../lib/firebase";


type AuthMode =
  | "login"
  | "signup";


export default function AuthPage() {
  const router = useRouter();

  const [
    mode,
    setMode,
  ] = useState<AuthMode>(
    "login"
  );

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );


  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    setError(null);


    if (
      mode === "signup" &&
      password !==
        confirmPassword
    ) {
      setError(
        "Passwords do not match."
      );

      return;
    }


    if (
      password.length < 6
    ) {
      setError(
        "Password must be at least 6 characters."
      );

      return;
    }


    try {
      setLoading(true);


      if (
        mode === "signup"
      ) {
        await createUserWithEmailAndPassword(
          auth,
          email.trim(),
          password
        );

      } else {
        await signInWithEmailAndPassword(
          auth,
          email.trim(),
          password
        );
      }


      router.push("/");

    } catch (err) {
      console.error(err);


      if (
        err instanceof FirebaseError
      ) {
        setError(
          firebaseErrorMessage(
            err.code
          )
        );

      } else {
        setError(
          "Something went wrong. Please try again."
        );
      }

    } finally {
      setLoading(false);
    }
  }


  function switchMode(
    nextMode: AuthMode
  ) {
    setMode(nextMode);
    setError(null);
    setPassword("");
    setConfirmPassword("");
  }


  return (
    <main className="flex min-h-screen items-center justify-center bg-[#070B14] px-6 py-12 text-white">

      <div className="w-full max-w-md">

        <div className="mb-8 text-center">

          <p className="text-sm uppercase tracking-[0.22em] text-blue-400">
            MissionGuard AI
          </p>

          <h1 className="mt-3 text-3xl font-bold">
            {mode === "login"
              ? "Welcome Back"
              : "Create Your Account"}
          </h1>

          <p className="mt-3 text-sm leading-6 text-gray-500">
            {mode === "login"
              ? "Sign in to access your MissionGuard dashboard and saved assessments."
              : "Create an account to save mission assessments, simulations, and reports."}
          </p>

        </div>


        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-2xl">

          <div className="mb-6 grid grid-cols-2 rounded-xl bg-black/20 p-1">

            <button
              type="button"
              onClick={() =>
                switchMode(
                  "login"
                )
              }
              className={`rounded-lg px-4 py-2.5 text-sm font-medium transition ${
                mode === "login"
                  ? "bg-blue-500 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Sign In
            </button>


            <button
              type="button"
              onClick={() =>
                switchMode(
                  "signup"
                )
              }
              className={`rounded-lg px-4 py-2.5 text-sm font-medium transition ${
                mode === "signup"
                  ? "bg-blue-500 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Sign Up
            </button>

          </div>


          <form
            onSubmit={
              handleSubmit
            }
            className="space-y-5"
          >

            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm text-gray-400"
              >
                Email address
              </label>

              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(
                  event
                ) =>
                  setEmail(
                    event.target
                      .value
                  )
                }
                placeholder="you@example.com"
                className="w-full rounded-xl border border-white/10 bg-[#0C1220] px-4 py-3 text-sm text-white outline-none transition placeholder:text-gray-600 focus:border-blue-400/60"
              />
            </div>


            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm text-gray-400"
              >
                Password
              </label>

              <input
                id="password"
                type="password"
                required
                minLength={6}
                autoComplete={
                  mode ===
                  "login"
                    ? "current-password"
                    : "new-password"
                }
                value={password}
                onChange={(
                  event
                ) =>
                  setPassword(
                    event.target
                      .value
                  )
                }
                placeholder="Minimum 6 characters"
                className="w-full rounded-xl border border-white/10 bg-[#0C1220] px-4 py-3 text-sm text-white outline-none transition placeholder:text-gray-600 focus:border-blue-400/60"
              />
            </div>


            {mode ===
              "signup" && (
              <div>
                <label
                  htmlFor="confirmPassword"
                  className="mb-2 block text-sm text-gray-400"
                >
                  Confirm password
                </label>

                <input
                  id="confirmPassword"
                  type="password"
                  required
                  minLength={6}
                  autoComplete="new-password"
                  value={
                    confirmPassword
                  }
                  onChange={(
                    event
                  ) =>
                    setConfirmPassword(
                      event.target
                        .value
                    )
                  }
                  placeholder="Repeat your password"
                  className="w-full rounded-xl border border-white/10 bg-[#0C1220] px-4 py-3 text-sm text-white outline-none transition placeholder:text-gray-600 focus:border-blue-400/60"
                />
              </div>
            )}


            {error && (
              <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
                {error}
              </div>
            )}


            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-500 px-5 py-3 font-semibold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Please wait..."
                : mode ===
                    "login"
                  ? "Sign In"
                  : "Create Account"}
            </button>

          </form>


          <p className="mt-6 text-center text-xs leading-5 text-gray-600">
            MissionGuard AI is an educational
            space-weather decision-support
            prototype.
          </p>

        </div>

      </div>
    </main>
  );
}


function firebaseErrorMessage(
  code: string
) {
  switch (code) {
    case "auth/email-already-in-use":
      return "An account already exists with this email.";

    case "auth/invalid-email":
      return "Enter a valid email address.";

    case "auth/weak-password":
      return "Choose a stronger password.";

    case "auth/invalid-credential":
      return "Incorrect email or password.";

    case "auth/user-not-found":
      return "No account exists with this email.";

    case "auth/wrong-password":
      return "Incorrect email or password.";

    case "auth/too-many-requests":
      return "Too many attempts. Please try again later.";

    case "auth/network-request-failed":
      return "Network connection failed. Check your internet connection.";

    default:
      return "Authentication failed. Please try again.";
  }
}
