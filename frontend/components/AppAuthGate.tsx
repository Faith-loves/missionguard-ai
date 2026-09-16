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
  usePathname,
  useRouter,
} from "next/navigation";

import {
  auth,
} from "../lib/firebase";


export default function AppAuthGate({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  const [checking, setChecking] =
    useState(true);

  const [allowed, setAllowed] =
    useState(false);


  useEffect(() => {
    // The login/signup page must stay public.
    if (pathname === "/auth") {
      setAllowed(true);
      setChecking(false);
      return;
    }


    const unsubscribe =
      onAuthStateChanged(
        auth,
        (user) => {
          if (!user) {
            setAllowed(false);
            setChecking(false);

            router.replace(
              "/auth"
            );

            return;
          }

          setAllowed(true);
          setChecking(false);
        }
      );


    return unsubscribe;

  }, [
    pathname,
    router,
  ]);


  if (
    pathname === "/auth"
  ) {
    return children;
  }


  if (
    checking ||
    !allowed
  ) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#070B14] text-white">

        <div className="text-center">

          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-white/10 border-t-blue-400" />

          <p className="mt-4 text-sm text-gray-500">
            Checking your account...
          </p>

        </div>

      </div>
    );
  }


  return children;
}
