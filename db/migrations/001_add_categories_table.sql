-- Create the categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    type VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Insert default categories
INSERT INTO categories (name, type) VALUES
('Food & Dining', 'Discretionary Expenses'),
('Rent & Housing', 'Necessary Expenses'),
('Transportation', 'Necessary Expenses'),
('Shopping', 'Discretionary Expenses'),
('Groceries', 'Necessary Expenses'),
('Hardware', 'Discretionary Expenses'),
('Entertainment', 'Discretionary Expenses'),
('Bills & Utilities', 'Necessary Expenses'),
('Income', 'Income'),
('Insurance', 'Necessary Expenses'),
('Healthcare', 'Necessary Expenses'),
('Donation', 'Discretionary Expenses'),
('Other', 'Special'),
('Uncategorized', 'Special')
ON CONFLICT (name) DO NOTHING;

-- Add category_id to transactions table
ALTER TABLE transactions
ADD COLUMN category_id UUID;

-- Add foreign key constraint to transactions table
ALTER TABLE transactions
ADD CONSTRAINT fk_category
FOREIGN KEY (category_id)
REFERENCES categories(id)
ON DELETE SET NULL;

-- Migrate existing categories (optional, if you have data)
-- This assumes you want to keep existing category names and convert them to UUIDs
-- INSERT INTO categories (name)
-- SELECT DISTINCT category FROM transactions WHERE category IS NOT NULL
-- ON CONFLICT (name) DO NOTHING;

-- UPDATE transactions
-- SET category_id = (SELECT id FROM categories WHERE name = transactions.category)
-- WHERE category IS NOT NULL;

-- Drop the old category column from transactions table
ALTER TABLE transactions
DROP COLUMN category;

-- Add category_id to budgets table
ALTER TABLE budgets
ADD COLUMN category_id UUID;

-- Add foreign key constraint to budgets table
ALTER TABLE budgets
ADD CONSTRAINT fk_budget_category
FOREIGN KEY (category_id)
REFERENCES categories(id)
ON DELETE SET NULL;

-- Migrate existing categories for budgets (optional, if you have data)
-- INSERT INTO categories (name)
-- SELECT DISTINCT category FROM budgets WHERE category IS NOT NULL
-- ON CONFLICT (name) DO NOTHING;

-- UPDATE budgets
-- SET category_id = (SELECT id FROM categories WHERE name = budgets.category)
-- WHERE category IS NOT NULL;

-- Drop the old category column from budgets table
ALTER TABLE budgets
DROP COLUMN category;

-- Update updated_at triggers for new tables/columns if necessary
-- (Assuming you have a generic trigger function for updated_at)
-- CREATE OR REPLACE FUNCTION update_updated_at_column()
-- RETURNS TRIGGER AS $$
-- BEGIN
--    NEW.updated_at = now();
--    RETURN NEW;
-- END;
-- $$ language 'plpgsql';

-- CREATE TRIGGER update_categories_updated_at
-- BEFORE UPDATE ON categories
-- FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
