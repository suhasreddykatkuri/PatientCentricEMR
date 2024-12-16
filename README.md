
# Patient-Centric EMR Sharing System

## Overview
The Patient-Centric EMR Sharing System is designed to securely share Electronic Medical Records (EMRs) between healthcare providers using a **dual blockchain architecture**. The system implements **Elliptic Curve Cryptography (ECC)** for secure data encryption and verification, combined with smart contracts for blockchain-based storage and retrieval. This project leverages both **SUPchain** and **MEDchain** blockchains to store and manage EMRs efficiently.

## Key Features
1. **Dual Blockchain Architecture**: Utilizes two separate blockchains (SUPchain and MEDchain) for data redundancy and security.
2. **ECC Encryption**: Uses Elliptic Curve Cryptography (NIST256p) for encrypting and signing EMRs before uploading to the blockchain.
3. **Smart Contracts**: Interacts with Ethereum-based smart contracts for data storage and retrieval.
4. **Web Interface**: A simple web-based interface built using Flask for uploading and retrieving EMRs.
5. **Base64 Image Encoding**: Converts images into Base64 format for blockchain storage.

---

## Architecture

### Dual Blockchain Integration
- **SUPchain**: Handles standard EMR storage and retrieval.
- **MEDchain**: Used for storing encrypted EMR data for specific use cases, ensuring data integrity and redundancy.

### ECC (Elliptic Curve Cryptography)
- ECC (NIST256p) is used to encrypt EMR data before uploading it to the blockchain.
- Provides secure, lightweight encryption suitable for blockchain applications.
- Ensures that EMR data can only be decrypted and verified using the ECC public key.

### Smart Contracts
Smart contracts deployed on Ethereum provide the following functionalities:
1. **Data Storage**: Securely stores encrypted EMR data.
2. **Data Retrieval**: Retrieves encrypted data for authorized users.

---

## Workflow

### **1. Uploading an EMR**
- **Patient ID** and **Blockchain Type** (SUPchain or MEDchain) are provided via the web interface.
- The selected image file is converted to **Base64** format.
- The Base64 data is **encrypted** using ECC.
- The encrypted data is stored on the selected blockchain using smart contracts.

### **2. Retrieving an EMR**
- The **Patient ID** and **Blockchain Type** are provided via the web interface.
- Encrypted data is retrieved from the blockchain using smart contracts.
- The data is **verified and decrypted** using ECC.
- The decrypted data is converted back to an image and served to the user.

---

## Technology Stack

| **Component**            | **Technology**                    |
|--------------------------|----------------------------------|
| Backend                  | Python (Flask)                   |
| Blockchain Interaction   | Web3.py                          |
| Encryption               | ECC (NIST256p Curve)             |
| Smart Contracts          | Solidity                         |
| Blockchain Network       | Ethereum (Sepolia Testnet)       |
| Blockchain Provider      | Infura                           |
| Frontend                 | HTML, CSS (via Flask Templates)  |
| Data Encoding            | Base64                          |

---

## Installation Instructions

### Prerequisites
1. Install Python 3.11 or above.
2. Create an account on [Infura](https://infura.io) and set up a Sepolia endpoint.
3. Install dependencies:
   ```bash
   pip install flask web3 ecdsa
   ```

4. Deploy the Smart Contracts to the Sepolia Testnet.
   - Replace `0xSupChainContractAddress` and `0xMedChainContractAddress` with the deployed contract addresses.

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/patient-centric-emr.git
   cd patient-centric-emr
   ```
2. Replace the following placeholders in the code:
   - `YOUR_INFURA_PROJECT_ID` with your Infura project ID.
   - `YOUR_PRIVATE_KEY` with your Ethereum private key.
3. Run the application:
   ```bash
   python main.py
   ```
4. Open the Flask application on `http://127.0.0.1:5000`.

---

## How to Use

### Upload an EMR
1. Go to `http://127.0.0.1:5000`.
2. Enter the **Patient ID**.
3. Choose the blockchain: `SUPchain` or `MEDchain`.
4. Upload the image file.
5. Click **Upload**.

### Retrieve an EMR
1. Go to `http://127.0.0.1:5000`.
2. Enter the **Patient ID**.
3. Choose the blockchain: `SUPchain` or `MEDchain`.
4. Click **Retrieve**.

---

## Smart Contract ABI
The smart contracts include two primary functions:
1. **storeData**: To store encrypted EMR data on the blockchain.
2. **getData**: To retrieve stored data using a unique identifier.

### Example ABI
```json
[
    {
        "constant": false,
        "inputs": [
            {"name": "_identifier", "type": "string"},
            {"name": "_data", "type": "string"}
        ],
        "name": "storeData",
        "outputs": [],
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {"name": "_identifier", "type": "string"}
        ],
        "name": "getData",
        "outputs": [
            {"name": "", "type": "string"}
        ],
        "type": "function"
    }
]
```

---

## Security Considerations
1. **Private Key Security**: Store the private key securely using environment variables.
2. **ECC Encryption**: Ensures data integrity and confidentiality before storing on the blockchain.
3. **Smart Contract Authorization**: Access to EMRs is controlled through unique patient IDs.

