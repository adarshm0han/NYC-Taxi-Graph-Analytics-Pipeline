Build the docker file using: docker build --build-arg GITHUB_TOKEN=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 -t project1phase1 .

Run the docker file using: docker run -it -p 7474:7474 -p 7687:7687 project1phase1

Please test interface.py in your local machine's virtual environemt:-

To create virtual environment: python3 -m venv myenv
To activate virtual environment: source myenv/bin/activate
Install neo4j: pip install neo4j
Install requests: pip install requests
Run tester.py: python3 tester.py
