import React, { createContext, useContext, useState } from 'react';

const UserContext = createContext(null);

// HARD CODING USER INFO UNTIL LOGIN SCREEN
const DEFAULT_STATE = {
  username: 'ee.bolton',
  isLoggedIn: true,
};

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(DEFAULT_STATE);
    return (
        <UserContext.Provider value={{ user, setUser }}>
            {children}
        </UserContext.Provider>
    );
};

export const useUser = () => useContext(UserContext);
