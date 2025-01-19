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

// const firebaseConfig = {
//   apiKey: "AIzaSyAPhxFV07K-Fhf3blPY9RIkavbRsYpJEx8",
//   authDomain: "desktop-app-distribution.firebaseapp.com",
// projectId: "desktop-app-distribution",
// storageBucket: "desktop-app-distribution.firebasestorage.app",
// messagingSenderId: "30202797598",
// appId: "1:30202797598:web:45656c7ecd9479d832180f",
// measurementId: "G-16KJ2FRY4C"
// };

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const initFirebase = () => {
  return app;
};
