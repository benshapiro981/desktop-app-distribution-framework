// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration


const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FBASE_MEASUREMENT_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const initFirebase = () => {
  return app;
};
