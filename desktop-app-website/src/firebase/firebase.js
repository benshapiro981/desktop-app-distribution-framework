import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FBASE_API_KEY,

  authDomain: process.env.REACT_APP_FBASE_AUTH_DOMAIN,

  projectId: process.env.REACT_APP_FBASE_PROJECT_ID,

  storageBucket: process.env.REACT_APP_FBASE_STORAGE_BUCKET,

  messagingSenderId: process.env.REACT_APP_FBASE_MESSAGING_SENDER_ID,

  appId: process.env.REACT_APP_FBASE_APP_ID,

  measurementId: process.env.REACT_APP_FBASE_MEASUREMENT_ID

  };

const app = initializeApp(firebaseConfig);
const auth = getAuth(app)



export { app, auth };
