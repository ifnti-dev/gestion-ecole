docker compose down
docker system prune
docker compose build
docker compose up -d
#docker exec -it ifnti_app sh init_db.sh

#psql -U ifnti -d ifnti
#docker exec -it db bash
#docker volume rm $(docker volume ls -q)