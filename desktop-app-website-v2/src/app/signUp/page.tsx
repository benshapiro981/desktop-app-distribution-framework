"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { initFirebase } from "@/firebase";
import { getAuth, createUserWithEmailAndPassword } from "firebase/auth";

export default function signIn() {

    const router = useRouter();

    const app = initFirebase();
    const auth = getAuth(app);

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [isSigningUp, setIsSigningUp] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");

    function validatePasswords(p: string, cp: string) {
        return p === cp
    }

    async function onClickSubmit(e: any) {
        console.log("sign up ");
        e.preventDefault();
        if (!isSigningUp) {
            setIsSigningUp(true);
            try {
                if (!validatePasswords(password, confirmPassword)) {
                    throw new Error("password and confirm password do not match");
                }
                const result = await createUserWithEmailAndPassword(auth, email, password);
                const user = result.user;

                if (user) {
                    router.push("/account");
                }
            } catch (e: any) {
                setErrorMsg(e.message);

            } finally {
                setIsSigningUp(false);
            }
        }
    }

    function onClickSignIn() {
        router.replace("/signIn")
    }

    function goBackHome() {
        router.back();
    }

    return (
        <>
            <button
                onClick={goBackHome}
                className="bg-blue-600 p-4 px-6 text-lg rounded-lg hover:bg-blue-700 shadow-lg"
            >
                <div className="flex gap-2 items-center align-middle">
                    go home
                </div>
            </button>
            <div className="text-5xl md:text-6xl font-bold">
                <span className="text-transparent bg-clip-text bg-gradient-to-tr from-teal-400 to-blue-500">
                    my app
                </span>
            </div>
            <div className="text-xl md:text-2xl font-light mb-8">
                Welcome! Please enter details below to create an account
            </div>
            <form
                onSubmit={onClickSubmit}
            >
                <div className="text-xl font-light">
                    email
                </div>
                <input className="text-black"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => { setEmail(e.target.value) }}
                ></input>
                <div className="text-xl font-light">
                    pass
                </div>
                <input className="text-black"
                    disabled={isSigningUp}
                    type="password"
                    autoComplete="new-password"
                    required
                    value={password}
                    onChange={(e) => { setPassword(e.target.value) }}
                ></input>
                <div className="text-xl font-light">
                    confirm pass
                </div>
                <input className="text-black"
                    disabled={isSigningUp}
                    type="password"
                    autoComplete="off"
                    required
                    value={confirmPassword}
                    onChange={(e) => { setConfirmPassword(e.target.value) }}
                ></input>

                {errorMsg && (
                    <span className='text-red-600 font-bold'>{errorMsg}</span>
                )}

                {/* <button
        
        onClick={onClickSubmit}
        className="bg-blue-600 p-4 px-6 text-lg rounded-lg hover:bg-blue-700 shadow-lg"
      > */}
                <button
                    type="submit"
                    disabled={isSigningUp}
                    className={`w-full px-4 py-2 text-white font-medium rounded-lg ${isSigningUp ? 'bg-gray-300 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-xl transition duration-300'}`}
                >
                    <div className="flex gap-2 items-center align-middle">
                        sign up
                    </div>
                </button>
            </form>
            <div className="text-xl md:text-2xl font-light mb-8">
                OR
            </div>
            <button
                onClick={onClickSignIn}
                className="bg-blue-600 p-4 px-6 text-lg rounded-lg hover:bg-blue-700 shadow-lg"
            >
                <div className="flex gap-2 items-center align-middle">
                    click here to sigin in with existing account
                </div>
            </button>
        </>
    );
}