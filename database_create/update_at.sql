CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER tr_chamada_update_timestamp
BEFORE UPDATE ON chamada
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
