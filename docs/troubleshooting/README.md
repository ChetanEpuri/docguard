# Troubleshooting

This section provides solutions to common issues encountered while running the application.

## Common Issues

### Issue: Application fails to start
**Symptom:** The container exits immediately with code `1`.
**Cause:** Missing environment variables.
**Solution:** Ensure all required environment variables are present in the `.env` file. Check the container logs for specific missing variables.

### Issue: Database connection timeout
**Symptom:** API requests return `503 Service Unavailable`.
**Cause:** The application cannot reach the database.
**Solution:** Verify that the database service is running and accessible from the application network. Check network policies and firewall rules.

## Gathering Logs
To extract logs for debugging, run:
```bash
docker logs <container_id> > app_error.log
```
Attach this log file when requesting support.
