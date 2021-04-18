# COVID-19 Twitter Data Sentiment Analysis using Spark and Kafka
* All commands are issued in the ```fyp-kafka``` namespace.

## Deploying Kafka Cluster
* Follow the readmes inside the ```kafka-deployment``` directory for deploying Kafka and Zookeeper. 
* Zookeeper should be deployed prior to deployment of Kafka.

## Twitter Producer

* Create a docker image of the twitter producer using the following commands

```sh
cd twitter-producer
sudo docker build -t twitter-producer .
```


* Once the image is built, use the following Kubernetes commands we can deploy a pod  and a service for the twitter-producer

```sh
sudo docker create $imageId
sudo docker commit $hash 10.3.2.48:5000/twitter-producer
sudo docker push 10.3.2.48:5000/twitter-producer
kubectl apply -f config.yaml
```


## Dash Frontend

* SSH into the master node on port ```8050```

* Create a docker image of the dash frontend using the following commands

```sh
cd fyp-dash
sudo docker build -t fyp-dash .
```

* Once the image is built, use the following Kubernetes commands we can deploy a pod  and a service for the dash frontend.

```sh
sudo docker create $imageId
sudo docker commit $hash 10.3.2.48:5000/fyp-dash
sudo docker push 10.3.2.48:5000/fyp-dash
kubectl apply -f config.yaml
```

* Run the following command to access the Dash UI at ```localhost:8050```:
```sh
kubectl port-forward svc/fyp-dash-service 8050:8050
```

## Spark Cluster Deployment

* First start a python server on your local machine in this directory:
```sh
python3 -m http.server 8000
```

* Use ngrok to make this globally accessible:
```sh
ngrok http 8000
```

* The Spark file would be avaible at the https://ngrok_address/SparkStreaming/main.py

* Download and extract the spark distribution on the master node by using the following command:
```sh
wget https://www.apache.org/dyn/closer.lua/spark/spark-2.4.7/spark-2.4.7-bin-hadoop2.7.tgz
tar -xvf spark-2.4.7-bin-hadoop2.7.tgz
```

* Create a new service account for Spark and grant it rbac to manage resources:
```sh
$ kubectl create serviceaccount spark
$ kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=fyp-kafka
```

* Execute the following command inside the Spark directory on the master node while updating the ngrok address:

```sh
bin/spark-submit \
      --deploy-mode cluster \
      --master k8s://https://10.4.2.37:6443 \
      --conf spark.executor.memory=500m \
      --conf spark.driver.memory=4G \
      --conf spark.driver.cores=4 \
      --conf spark.executor.cores=2 \
      --conf spark.executor.instances=5 \
      --conf spark.app.name=spark-full \
      --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
      --conf spark.kubernetes.container.image=gcr.io/spark-operator/spark-py:v2.4.5 \
      --conf spark.kubernetes.namespace=fyp-kafka \
      --conf spark.kubernetes.pyspark.pythonVersion=3 \
      --jars https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-8-assembly_2.11/2.4.5/spark-streaming-kafka-0-8-assembly_2.11-2.4.5.jar \
      https://ngrok_address/SparkStreaming/main.py
```

* Run the following command on the master node to find the pod name of the Spark driver.
```sh
kubectl get pods
```

* SSH into the master node on port ```4040``` and run the following command to access the Spark UI at ```localhost:4040```:
```sh
kubectl port-forward $spark_driver_pod_name 4040:4040
```

# Machine Learning

Follow the ```model-training/training.ipynb``` jupyter notebook to train and save the machine learning model.