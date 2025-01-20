"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { initFirebase } from "@/firebase";
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";

export default function signIn() {

    const router = useRouter();

    const app = initFirebase();
    const auth = getAuth(app);


    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isSigningIn, setIsSigningIn] = useState(false);
    const [errormessage, setErrormessage] = useState("");


    // function onClickSignIn() {
    //     console.log("sign in ");
    // }

    function onClickSignUp() {
        router.replace("/signUp")
    }

    function goBackHome() {
        router.back();
    }

    async function onSubmitForm(e: any) {
        e.preventDefault();
        if (!isSigningIn) {
            setIsSigningIn(true);
            try {
                const result = await signInWithEmailAndPassword(auth, email, password);
                const user = result.user;

                if (user) {
                    router.push("/account")
                }
            } catch (e: any) {

                setErrormessage(e.message);
            } finally {
                setIsSigningIn(false);
            }

        }
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
                Welcome back, please sign in
            </div>
            <form
                onSubmit={onSubmitForm}
            >
                <div className="text-xl font-light">
                    email
                </div>
                <input
                    className="text-black"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => { setEmail(e.target.value) }}
                ></input>
                <div className="text-xl font-light">
                    pass
                </div>
                <input
                    className="text-black"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => { setPassword(e.target.value) }}
                ></input>

                {errormessage && (
                    <span className='text-red-600 font-bold'>{errormessage}</span>
                )}

                {/* <button
        onClick={onClickSignIn}
        className="bg-blue-600 p-4 px-6 text-lg rounded-lg hover:bg-blue-700 shadow-lg"
      > */}
                <button
                    type="submit"
                    disabled={isSigningIn}
                    className={`w-full px-4 py-2 text-white font-medium rounded-lg ${isSigningIn ? 'bg-gray-300 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-xl transition duration-300'}`}
                >
                    <div className="flex gap-2 items-center align-middle">
                        sign in
                    </div>
                </button>
            </form>
            <div className="text-xl md:text-2xl font-light mb-8">
                OR
            </div>
            <button
                onClick={onClickSignUp}
                className="bg-blue-600 p-4 px-6 text-lg rounded-lg hover:bg-blue-700 shadow-lg"
            >
                <div className="flex gap-2 items-center align-middle">
                    click here to create account
                </div>
            </button>



        </>
    );
}