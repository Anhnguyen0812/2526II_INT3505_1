import express from 'express';
import swaggerUi from 'swagger-ui-express';
import swaggerJsdoc from 'swagger-jsdoc';
import userRoutes from './routes/userRoutes';

const app = express();
const PORT = 3000;

const swaggerOptions = {
    definition: {
        openapi: '3.0.0',
        info: {
            title: 'User Management API',
            version: '1.0.0',
            description: 'Week 2 Practice API - Managing users and posts',
        },
        servers: [
            {
                url: `http://localhost:${PORT}`,
            },
        ],
    },
    apis: ['./src/routes/*.ts'], // Path to the API docs
};

const swaggerDocs = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));

// Middleware to parse JSON request bodies
app.use(express.json());

// Use defined routes
app.use('/api', userRoutes);

// Default route (Fallback for 404 error)
app.use((req, res) => {
    res.status(404).json({
        message: "URL not found on this server",
        status: 404
    });
});

app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
    console.log('Available endpoints:');
    console.log('1. [GET] /api/users');
    console.log('2. [GET] /api/users/:id');
    console.log('3. [POST] /api/users');
    console.log('4. [PATCH] /api/users/:id');
    console.log('5. [DELETE] /api/users/:id');
    console.log('Swagger UI: http://localhost:3000/api-docs');
});
