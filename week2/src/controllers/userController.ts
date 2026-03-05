import { Request, Response } from 'express';
import * as fs from 'fs';
import * as path from 'path';

const dataPath = path.join(__dirname, '../data/data.json');

const readData = () => {
    const data = fs.readFileSync(dataPath, 'utf8');
    return JSON.parse(data);
};

const writeData = (data: any) => {
    fs.writeFileSync(dataPath, JSON.stringify(data, null, 2), 'utf8');
};

export const UserController = {
    // 1. GET: Fetch all users
    getAllUsers: (req: Request, res: Response) => {
        try {
            const data = readData();
            res.status(200).json(data.users);
        } catch (error) {
            res.status(500).json({ message: "Internal Server Error", error });
        }
    },

    // 2. GET: Fetch a single user by ID
    getUserById: (req: Request, res: Response) => {
        try {
            const data = readData();
            const { id } = req.params;
            if (!id) return res.status(400).json({ message: "User ID is required" });

            const userId = typeof id === 'string' ? parseInt(id) : parseInt(id[0] || '0');

            const user = data.users.find((u: any) => u.id === userId);
            if (!user) {
                return res.status(404).json({ message: "User not found" });
            }
            res.status(200).json(user);
        } catch (error) {
            res.status(500).json({ message: "Internal Server Error", error });
        }
    },

    // 3. POST: Create a new user
    createUser: (req: Request, res: Response) => {
        try {
            const data = readData();
            const newUser = {
                id: data.users.length + 1,
                ...req.body
            };
            data.users.push(newUser);
            writeData(data);
            res.status(201).json(newUser);
        } catch (error) {
            res.status(400).json({ message: "Invalid data provided", error });
        }
    },

    // 4. PATCH: Update user's email
    updateUserEmail: (req: Request, res: Response) => {
        try {
            const { email } = req.body;
            const { id } = req.params;
            if (!id) return res.status(400).json({ message: "User ID is required" });
            if (!email) return res.status(400).json({ message: "Email is required for update" });

            const userId = typeof id === 'string' ? parseInt(id) : parseInt(id[0] || '0');
            const data = readData();
            const userIndex = data.users.findIndex((u: any) => u.id === userId);
            
            if (userIndex === -1) {
                return res.status(404).json({ message: "User not found" });
            }

            data.users[userIndex].email = email;
            writeData(data);
            res.status(200).json(data.users[userIndex]);
        } catch (error) {
            res.status(500).json({ message: "Internal Server Error", error });
        }
    },

    // 5. DELETE: Remove a user
    deleteUser: (req: Request, res: Response) => {
        try {
            const { id } = req.params;
            if (!id) return res.status(400).json({ message: "User ID is required" });

            const userId = typeof id === 'string' ? parseInt(id) : parseInt(id[0] || '0');
            const data = readData();
            const initialLength = data.users.length;
            data.users = data.users.filter((u: any) => u.id !== userId);
            
            if (data.users.length === initialLength) {
                return res.status(404).json({ message: "User not found for deletion" });
            }

            writeData(data);
            res.status(200).json({ message: "User deleted successfully" });
        } catch (error) {
            res.status(500).json({ message: "Internal Server Error", error });
        }
    }
};
