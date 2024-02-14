docker compose down
docker volume rm $(docker volume ls -q)
docker system prune
docker compose build 
docker compose up -d
#docker exec -it ifnti_app sh init_db.sh
#psql -U ifnti -d ifnti
#docker exec -it db bash
# docker exec -it web