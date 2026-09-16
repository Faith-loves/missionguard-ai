"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  User,
  onAuthStateChanged,
  signOut,
} from "firebase/auth";

import {
  useRouter,
} from "next/navigation";

import {
  auth,
} from "../lib/firebase";


export default function UserAccount() {
  const router = useRouter();

  const [
    user,
    setUser,
  ] = useState<User | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(true);


  useEffect(() => {
    const unsubscribe =
      onAuthStateChanged(
        auth,
        (firebaseUser) => {
          setUser(
            firebaseUser
          );

          setLoading(false);
        }
      );

    return unsubscribe;
  }, []);


  async function handleSignOut() {
    await signOut(auth);

    router.push(
      "/auth"
    );
  }


  if (loading) {
    return (
      <div className="h-9 w-28 animate-pulse rounded-xl bg-white/5" />
    );
  }


  if (!user) {
    return (
      <button
        type="button"
        onClick={() =>
          router.push(
            "/auth"
          )
        }
        className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm transition hover:bg-white/10"
      >
        Sign In
      </button>
    );
  }


  return (
    <div className="flex items-center gap-3">

      <div className="hidden text-right sm:block">

        <p className="text-xs text-gray-500">
          Signed in as
        </p>

        <p className="max-w-[200px] truncate text-sm font-medium text-gray-200">
          {user.email}
        </p>

      </div>


      <button
        type="button"
        onClick={
          handleSignOut
        }
        className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-300 transition hover:border-red-400/30 hover:bg-red-500/10 hover:text-red-300"
      >
        Sign Out
      </button>

    </div>
  );
}
