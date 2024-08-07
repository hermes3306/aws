import mindsdb_native
import pandas as pd
from sqlalchemy import create_engine, text

# Connect to PostgreSQL
engine = create_engine('postgresql://username:password@localhost:5432/your_database')

# Create schema and populate data
schema_and_data = """
-- Create tables
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    registration_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    user_id INTEGER REFERENCES users(user_id),
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_date DATE NOT NULL
);

-- Insert sample data
INSERT INTO users (username, email, registration_date) VALUES
    ('john_doe', 'john@example.com', '2023-01-01'),
    ('jane_smith', 'jane@example.com', '2023-02-15'),
    ('bob_johnson', 'bob@example.com', '2023-03-10')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO products (name, category, price) VALUES
    ('Laptop', 'Electronics', 999.99),
    ('Smartphone', 'Electronics', 599.99),
    ('Headphones', 'Electronics', 149.99),
    ('T-shirt', 'Clothing', 19.99),
    ('Jeans', 'Clothing', 49.99)
ON CONFLICT (product_id) DO NOTHING;

INSERT INTO orders (user_id, order_date, total_amount) VALUES
    (1, '2023-04-01', 1149.98),
    (2, '2023-04-05', 599.99),
    (3, '2023-04-10', 219.97),
    (1, '2023-04-15', 69.98),
    (2, '2023-04-20', 1049.98)
ON CONFLICT (order_id) DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
    (1, 1, 1, 999.99),
    (1, 3, 1, 149.99),
    (2, 2, 1, 599.99),
    (3, 3, 1, 149.99),
    (3, 4, 1, 19.99),
    (3, 5, 1, 49.99),
    (4, 4, 2, 19.99),
    (4, 5, 1, 49.99),
    (5, 1, 1, 999.99),
    (5, 4, 1, 19.99)
ON CONFLICT (order_item_id) DO NOTHING;

INSERT INTO reviews (product_id, user_id, review_text, rating, review_date) VALUES
    (1, 1, 'This laptop is amazing! Great performance and battery life.', 5, '2023-04-05'),
    (2, 2, 'The smartphone is good, but the camera could be better.', 4, '2023-04-10'),
    (3, 3, 'These headphones have excellent sound quality.', 5, '2023-04-15'),
    (4, 1, 'The t-shirt fabric is comfortable, but it shrunk after washing.', 3, '2023-04-20'),
    (5, 2, 'Perfect fit jeans, very durable.', 5, '2023-04-25'),
    (1, 3, 'Laptop is okay, but it runs a bit hot.', 3, '2023-05-01'),
    (2, 1, 'Great phone, love the features!', 5, '2023-05-05'),
    (3, 2, 'Headphones are comfortable, but the battery life is short.', 4, '2023-05-10'),
    (4, 3, 'Nice design, but the sizing is off.', 2, '2023-05-15'),
    (5, 1, 'These jeans are my new favorite!', 5, '2023-05-20')
ON CONFLICT (review_id) DO NOTHING;
"""

# Execute the schema and data insertion
with engine.connect() as connection:
    connection.execute(text(schema_and_data))
    connection.commit()

# Initialize MindsDB predictor
mdb = mindsdb_native.Predictor(name='product_review_predictor')

# Fetch review data from PostgreSQL
query = """
    SELECT 
        r.review_id,
        p.name AS product_name,
        p.category,
        u.username,
        r.review_text,
        r.rating,
        r.review_date
    FROM 
        reviews r
    JOIN 
        products p ON r.product_id = p.product_id
    JOIN 
        users u ON r.user_id = u.user_id
    ORDER BY 
        r.review_date
"""

df = pd.read_sql(query, engine)

# Display the current data
print("Current Review Data:")
print(df)

# Train the model
mdb.learn(
    from_data=df,
    to_predict='rating',
    ignore_columns=['review_id', 'review_date']
)

# Make predictions on existing data
predictions = mdb.predict(when_data=df)

print("\nPredictions for existing reviews:")
print(pd.DataFrame({
    'review_text': df['review_text'],
    'actual_rating': df['rating'],
    'predicted_rating': predictions['rating']
}))

# Example: Predict rating for a new review
new_review = pd.DataFrame({
    'product_name': ['Smartphone'],
    'category': ['Electronics'],
    'username': ['new_user'],
    'review_text': ['This smartphone has a great camera and long battery life, but the user interface is a bit confusing.']
})

new_review_prediction = mdb.predict(when_data=new_review)
print("\nPredicted rating for the new review:")
print(pd.DataFrame({
    'review_text': new_review['review_text'],
    'predicted_rating': new_review_prediction['rating']
}))

# Analyze feature importance
importance = mdb.get_model_data()['data_analysis']['target_columns_metadata']['rating']['importance']
print("\nFeature Importance:")
for feature, score in importance.items():
    print(f"{feature}: {score}")