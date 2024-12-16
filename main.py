from hashlib import sha256  # Importing SHA-256 hash function
import json  # Importing JSON for data handling
import base64  # Importing base64 for encoding/decoding data
from time import time  # Importing time for timestamping blocks
from web3 import Web3  # Importing Web3 for Ethereum blockchain interaction
from ecdsa import SigningKey, VerifyingKey, NIST256p  # Importing ECC for encryption
from flask import Flask, request, jsonify, send_file  # Flask for web server
import os  # Importing OS for file handling

# Connect to Ethereum Blockchain using Infura for Replit
INFURA_URL = 'https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID'  # Infura URL for Ethereum node
web3 = Web3(Web3.HTTPProvider(INFURA_URL))  # Connect to Ethereum via Web3

# Private key setup for signing transactions
PRIVATE_KEY = 'YOUR_PRIVATE_KEY'  # Replace with your Ethereum private key
ACCOUNT = web3.eth.account.from_key(PRIVATE_KEY).address  # Get the public address from the private key

# Flask App for Frontend
app = Flask(__name__)  # Initialize Flask application

# Blockchain class for creating and managing the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []  # Initialize an empty chain
        self.transactions = []  # Initialize an empty list for transactions
        self.create_block(proof=1, previous_hash='0')  # Create the genesis block

    def create_block(self, proof, previous_hash):
        """
        Creates a new block and appends it to the chain.
        :param proof: Proof of Work for the block
        :param previous_hash: Hash of the previous block
        """
        block = {
            'index': len(self.chain) + 1,  # Index of the block
            'timestamp': time(),  # Current timestamp
            'proof': proof,  # Proof of work
            'previous_hash': previous_hash,  # Hash of the previous block
            'transactions': self.transactions  # Transactions in the block
        }
        self.transactions = []  # Clear current transactions
        self.chain.append(block)  # Append the block to the chain
        return block

    def get_previous_block(self):
        """
        Returns the last block in the chain.
        """
        return self.chain[-1]

# ECC-Based Encryption and Decryption class
class ECCEncryption:
    def __init__(self):
        self.sk = SigningKey.generate(curve=NIST256p)  # Generate ECC private key
        self.vk = self.sk.get_verifying_key()  # Generate ECC public key

    def encrypt(self, message):
        """
        Signs a message using the private key.
        :param message: Message to be signed
        :return: Base64-encoded signature
        """
        signature = self.sk.sign(message.encode('utf-8'))  # Sign the message
        return base64.b64encode(signature).decode('utf-8')  # Encode in base64 for storage

    def verify_and_decrypt(self, message, signature):
        """
        Verifies the signature of a message.
        :param message: Original message
        :param signature: Signature to verify
        :return: Original message if valid, None otherwise
        """
        try:
            signature_bytes = base64.b64decode(signature)  # Decode the base64 signature
            self.vk.verify(signature_bytes, message.encode('utf-8'))  # Verify the signature
            return message  # Return the message if valid
        except Exception as e:
            return None  # Return None if verification fails

# Smart Contract Integration for blockchain storage and retrieval
class SmartContract:
    def __init__(self, contract_address, abi):
        self.contract = web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)  # Load contract

    def store_data(self, identifier, data):
        """
        Stores data on the blockchain.
        :param identifier: Identifier for the data
        :param data: Data to store
        """
        nonce = web3.eth.get_transaction_count(ACCOUNT)  # Get the transaction nonce
        transaction = self.contract.functions.storeData(identifier, data).build_transaction({
            'chainId': 11155111,  # Sepolia Testnet chain ID
            'gas': 2000000,  # Gas limit
            'gasPrice': web3.to_wei('10', 'gwei'),  # Gas price
            'nonce': nonce  # Transaction nonce
        })
        signed_tx = web3.eth.account.sign_transaction(transaction, PRIVATE_KEY)  # Sign the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)  # Send the signed transaction
        web3.eth.wait_for_transaction_receipt(tx_hash)  # Wait for transaction confirmation

    def retrieve_data(self, identifier):
        """
        Retrieves data from the blockchain.
        :param identifier: Identifier for the data
        :return: Retrieved data
        """
        return self.contract.functions.getData(identifier).call()  # Call the smart contract function

# Main EMR Sharing Class
class PatientCentricEMRSharing:
    def __init__(self, supchain_contract_address, medchain_contract_address, abi):
        self.supchain_contract = SmartContract(supchain_contract_address, abi)  # Smart contract for SUPchain
        self.medchain_contract = SmartContract(medchain_contract_address, abi)  # Smart contract for MEDchain
        self.ecc = ECCEncryption()  # ECC encryption for data security

    def image_to_base64(self, image_path):
        """
        Converts an image to base64.
        :param image_path: Path to the image file
        :return: Base64-encoded string
        """
        with open(image_path, "rb") as img_file:  # Open the image in binary mode
            return base64.b64encode(img_file.read()).decode('utf-8')  # Encode the image in base64

    def base64_to_image(self, base64_data, output_path):
        """
        Converts base64 data back to an image.
        :param base64_data: Base64-encoded string
        :param output_path: Path to save the output image
        """
        image_data = base64.b64decode(base64_data)  # Decode base64 data
        with open(output_path, "wb") as img_file:  # Save the image
            img_file.write(image_data)

    def upload_image(self, patient_id, image_path, chain="SUPchain"):
        """
        Uploads an image to the blockchain.
        :param patient_id: Identifier for the patient
        :param image_path: Path to the image file
        :param chain: Blockchain to use (SUPchain or MEDchain)
        :return: Success message
        """
        image_data = self.image_to_base64(image_path)  # Convert image to base64
        encrypted_data = self.ecc.encrypt(image_data)  # Encrypt the image data
        if chain == "SUPchain":
            self.supchain_contract.store_data(patient_id, encrypted_data)  # Store in SUPchain
        else:
            self.medchain_contract.store_data(patient_id, encrypted_data)  # Store in MEDchain
        return "Image uploaded successfully"

    def retrieve_image(self, patient_id, output_path, chain="SUPchain"):
        """
        Retrieves an image from the blockchain.
        :param patient_id: Identifier for the patient
        :param output_path: Path to save the output image
        :param chain: Blockchain to use (SUPchain or MEDchain)
        :return: Path to the saved image or None
        """
        if chain == "SUPchain":
            encrypted_data = self.supchain_contract.retrieve_data(patient_id)  # Retrieve from SUPchain
        else:
            encrypted_data = self.medchain_contract.retrieve_data(patient_id)  # Retrieve from MEDchain

        if encrypted_data:
            decrypted_data = self.ecc.verify_and_decrypt("image_data", encrypted_data)  # Verify and decrypt data
            if decrypted_data:
                self.base64_to_image(decrypted_data, output_path)  # Convert back to image
                return output_path  # Return the saved image path
        return None  # Return None if data not found

# Flask Routes
emr_sharing = PatientCentricEMRSharing("0xSupChainContractAddress", "0xMedChainContractAddress", [
    {
        "constant": False,
        "inputs": [
            {"name": "_identifier", "type": "string"},
            {"name": "_data", "type": "string"}
        ],
        "name": "storeData",
        "outputs": [],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_identifier", "type": "string"}
        ],
        "name": "getData",
        "outputs": [
            {"name": "", "type": "string"}
        ],
        "type": "function"
    }
])

@app.route('/')
def index():
    """
    Root route that renders HTML for uploading and retrieving images.
    """
    return """... (HTML code unchanged for brevity) ..."""

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Handles image upload via form data and uploads to blockchain.
    """
    patient_id = request.form['patient_id']
    chain = request.form['chain']
    file = request.files['file']
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)
    response = emr_sharing.upload_image(patient_id, file_path, chain)
    return jsonify({"message": response})

@app.route('/retrieve', methods=['POST'])
def retrieve_image():
    """
    Handles image retrieval from the blockchain and serves the image file.
    """
    patient_id = request.form['patient_id']
    chain = request.form['chain']
    output_path = os.path.join("downloads", f"retrieved_{patient_id}.png")
    result = emr_sharing.retrieve_image(patient_id, output_path, chain)
    if result:
        return send_file(result, mimetype='image/png')
    return jsonify({"error": "Image not found or access denied"})

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    app.run(debug=True, host="0.0.0.0", port=5000)
