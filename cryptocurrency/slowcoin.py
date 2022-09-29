import datetime
import hashlib
import json
import flask
from flask import Flask, jsonify, request
import sys
import requests
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions, }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def hash_block(self, block):
        encoded_block = json.dump(block, sort_keys=True).encode()

        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash_block(previous_block):
                return False
            proof = block['proof']
            previous_proof = previous_block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1

        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
        })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
        
    def add_nodes(self, address):
        parsedURL = urlparse(address)                                                                   #parses the url
        self.nodes.add(parsedURL.netloc) 
        
    def replace_chain(self):                                                                            #The longest chain wins and replaces the shorter chain in all of the nodes
        network = self.nodes
        logestChain = None
        maxlen = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/chain_get")
            if(response.status_code == 200):
                len = reponse.json()['length']
                chain = reponse.json()['chain']
                if(maxlen < len and self.chain_valid(chain)):
                    maxlen = len
                    logestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False


# Interacting with the blockchain, using Flask
#Web App with flask
app = Flask(__name__)

#Creating the initial address for the node on port 5000
nodeAddress = str(uuid4()).replace('-','')

#Making the blockchain instance
bchain = blockchain()

#Web page for mining a new block
@app.route('/block_mine', methods = ['GET'])
def block_mine():
    prev_block = bchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = bchain.pow(prev_proof)
    prev_hash = bchain.hash(prev_block)
    bchain.add_transactions(sender = nodeAddress, receiver = 'Naman', amount = 0.5)
    block = bchain.create_block(proof, prev_hash)
    response = {'msg': 'Successfully mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']
    }
    return jsonify(response), 200                                   #jsonify(response) converts the dictionary response to a json file and code 200 is an http status code which means the request was successful.

@app.route('/chain_get', methods = ['GET'])
def chain_get():
    response = {'chain': bchain.chain,
                'length': len(bchain.chain)
    }
    return jsonify(response), 200

@app.route('/if_valid', methods = ['GET'])                          #Checks if the chain is valid, basically just calls the chain_valid function from class blockchain
def if_valid():
    valid = bchain.chain_valid(bchain.chain)
    if(valid):
        response = {'msg:': "Blockchain is valid!"}
    else:
        response = {'msg:': "Blockchain is not valid!"}
    return jsonify(reponse), 200

@pp.route('/add_transaction', methods = ['POST'])                   #Add a transaction
def add_transaction():
        json = request.get_json()
        transaction_keys = ['senser','receiver','amount']
        if not all(key in json for key in transaction_keys):
            return 'Some fields are missing in the transaction', 400
        index = bchain.add_transactions(json['sender'], json['receiver'], json['amount'])
        response = {'message': f"Transaction added to Block {index}"}
        return jsonify(response), 201                               #201 is for creation, 200 can be used as well... does not matter


#Decentralizing the Blockchain

#Connecting the new Nodes
@app.route('/connect_node', methods = ['POST'])
def add_connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Node", 400
    for node in nodes:
        bchain.add_node(node)
    response = {'message':"The new nodes are connected!",
                'Total Nodes':list(bchain.nodes)
                }
    return jsonify(response), 201

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    if bchain.replace_chain():
        response = {'message':"The longest chain replaced the shorter chains in some nodes.",
                    'new_chain':bchain.chain}
    else:
        response = {'message':"All good! This chain is the largest one.",
                    'longest_chain':bchain.chain}
    return jsonify(response), 200




app.run(host = '0.0.0.0', port = 5000)                              #Runs the app publicly on your server
Footer