# WaqediAI Database Setup Script
# Run this after docker-compose up -d

Write-Host "WaqediAI Database Setup" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Wait for PostgreSQL to be ready
Write-Host "`nWaiting for PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Drop existing schemas to avoid conflicts
Write-Host "`nDropping existing schemas..." -ForegroundColor Yellow
docker exec -i waqedi-postgres psql -U waqedi -c "DROP SCHEMA IF EXISTS auth CASCADE; DROP SCHEMA IF EXISTS documents CASCADE; DROP SCHEMA IF EXISTS extraction CASCADE; DROP SCHEMA IF EXISTS language CASCADE; DROP SCHEMA IF EXISTS knowledge CASCADE; DROP SCHEMA IF EXISTS audit CASCADE;"

# Apply migrations
Write-Host "`nApplying migrations..." -ForegroundColor Green

Write-Host "  001_identity_schema.sql" -ForegroundColor White
Get-Content infra/docker/migrations/001_identity_schema.sql | docker exec -i waqedi-postgres psql -U waqedi

Write-Host "  002_documents_schema.sql" -ForegroundColor White
Get-Content infra/docker/migrations/002_documents_schema.sql | docker exec -i waqedi-postgres psql -U waqedi

Write-Host "  003_extraction_schema.sql" -ForegroundColor White
Get-Content infra/docker/migrations/003_extraction_schema.sql | docker exec -i waqedi-postgres psql -U waqedi

Write-Host "  004_language_schema.sql" -ForegroundColor White
Get-Content infra/docker/migrations/004_language_schema.sql | docker exec -i waqedi-postgres psql -U waqedi

Write-Host "  005_knowledge_schema.sql" -ForegroundColor White
Get-Content infra/docker/migrations/005_knowledge_schema.sql | docker exec -i waqedi-postgres psql -U waqedi

# Create MinIO bucket
Write-Host "`nCreating MinIO bucket..." -ForegroundColor Green
docker exec waqedi-minio mc alias set local http://localhost:9000 waqedi waqedi_dev_secret
docker exec waqedi-minio mc mb local/waqedi-documents --ignore-existing

Write-Host "`n✓ Database setup complete!" -ForegroundColor Green
Write-Host "`nServices ready:" -ForegroundColor Cyan
Write-Host "  PostgreSQL: localhost:5432"
Write-Host "  Redis:      localhost:6379"
Write-Host "  Qdrant:     localhost:6333"
Write-Host "  MinIO:      localhost:9000"
Write-Host "  Kafka:      localhost:9092"
