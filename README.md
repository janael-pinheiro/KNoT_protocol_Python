export AMQP_URL=amqp://knot:knot@localhost:5672

## Testing
poetry run coverage clean
poetry run coverage run -m pytest -s -v tests
poetry run coverage report
poetry run coverage xml


sudo docker run --rm --network=host -e SONAR_HOST_URL=http://127.0.0.1:9000/ -e SONAR_LOGIN=sqp_3ca62d658b1bab99e7c6d6ca504c91338a6276c1 -v /home/ajp/Documents/Projetos\ pessoais/knot-protocol-python/:/usr/src/ sonarsource/sonar-scanner-cli -Dsonar.projectKey=knot-protocol-sdk-python -Dsonar.sources=. -Dsonar.host.url=http://localhost:9000 -Dsonar.login=sqp_3ca62d658b1bab99e7c6d6ca504c91338a6276c1

