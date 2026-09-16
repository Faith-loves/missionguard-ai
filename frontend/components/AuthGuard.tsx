"use client";

import {
  ReactNode,
  useEffect,
  useState,
} from "react";

import {
  onAuthStateChanged,
} from "firebase/auth";

import {
  useRouter,
} from "next/navigation";

import {
  auth,
} from "../lib/firebase";


export default function AuthGuard({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();

  const [
    checking,
    setChecking,
  ] = useState(true);


  useEffect(() => {
    const unsubscribe =
      onAuthStateChanged(
        auth,
        (user) => {
          if (!user) {
            router.replace(
              "/auth"
            );

            return;
          }

          setChecking(false);
        }
      );

    return unsubscribe;
  }, [router]);


  if (checking) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#070B14] text-white">

        <div className="text-center">

          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-white/10 border-t-blue-400" />

          <p className="mt-4 text-sm text-gray-500">
            Checking your account...
          </p>

        </div>

      </main>
    );
  }


  return children;
}
