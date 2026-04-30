# Hardhat Tutorial

## Prerequisites

1. Install Metamask plugin using the instructions [here](https://www.respectedsir.com/ethlab/metamask.html). Copy the public key of the account.
2. Get some Sepolia ETH using the [Google Web3 faucet](https://cloud.google.com/application/web3/faucet/ethereum/sepolia) by pasting the public key from the previous step. You need to be signed in to your Gmail account.
3. Create a free account on [Alchemy](https://www.alchemy.com/) and create a new App. Copy the API key. It will be look like `Bx_F-oj-cOV-vLojT3Yfb`
4. Follow the instructions [here](https://v2.hardhat.org/tutorial/setting-up-the-environment) to setup the NodeJs environment

## Creating a new Hardhat project

1. Create a new directory and enter it by running the following commands (for Linux)
    ```
    mkdir hardhat-tutorial
    cd hardhat-tutorial
    ```
2. Initialize a new NodeJS project
    ```
    npm init -y
    ```

3. Install Hardhat
    ```
    npm install --save-dev hardhat@hh2
    ```
4. Initialize Hardhat
    ```
    npx hardhat init
    ```
    Choose `Create an empty hardhat.config.js` in the list of options. You should see a file called `hardhat.config.js` in the directory with contents
    ```Typescript
    /** @type import('hardhat/config').HardhatUserConfig */
    module.exports = {
        solidity: "0.8.28",
    };
    ```
5. Install Hardhat toolbox
    ```
    npm install --save-dev @nomicfoundation/hardhat-toolbox@hh2
    ```

## Compiling a contract

o add a contract and compile it using Hardhat, do the following:

1. In the project directory, create a `contracts` directory.
    ```
    mkdir contracts
    ```
2. Create a new file in the `contracts` directory called `HelloWorld.sol`.
3. Copy and paste the following code into `HelloWorld.sol`.

    ```javascript
    // SPDX-License-Identifier: MIT
    pragma solidity >=0.7.3;

    // Defines a contract named `HelloWorld`.
    contract HelloWorld {

        // Event emitted when update function is called
        event UpdatedMessages(string oldStr, string newStr);

        // Declares a state variable `message` of type `string`.
        string public message;

        // A constructor is a special function that is only executed upon contract creation.
        constructor(string memory initMessage) {
            message = initMessage;
        }

        // A public function that accepts a string argument and updates the `message` storage variable.
        function update(string memory newMessage) public {
            string memory oldMsg = message;
            message = newMessage;
            emit UpdatedMessages(oldMsg, newMessage);
        }
    }
    ```
4. Compile the contract by running the following command.
    ```
    npx hardhat compile
    ```
    You should see a message saying `Compiled 1 Solidity file successfully.`

    The command also creates a directory called `artifacts` that has some JSON files. The `HelloWorld.json` has the contract's code and **application binary interface (ABI)**. These will be used for contract deployment and interaction.


## Deploying a Contract
To deploy the `HelloWorld.sol` contract, do the following:

1. Install the dotenv package in your project directory.
    ```
    npm install dotenv --save
    ```
2. Create a file called `.env` in the project directory with the following contents. Fill in the API key and private key.
    ```
    API_URL = "https://eth-sepolia.g.alchemy.com/v2/<your-api-key>
    PRIVATE_KEY = "your-metamask-private-key"
    ```
    Follow [these instructions](https://support.metamask.io/configure/accounts/how-to-export-an-accounts-private-key) to export your private key from Metamask. The `API_URL` needs to be copied from your Alchemy account.

    > NOTE: If you are going to push the project code to a public Github/Gitlab repository, remember to add the `.env` file to your `.gitignore`.
4. Update the `hardhat.config.js` file to have the following content.
    ```javascript
    /** @type import('hardhat/config').HardhatUserConfig */

    require('dotenv').config();
    require("@nomicfoundation/hardhat-toolbox");

    const { API_URL, PRIVATE_KEY } = process.env;

    module.exports = {
      solidity: "0.8.28",
      defaultNetwork: "sepolia",
      networks: {
        sepolia: {
          url: API_URL,
          accounts: [PRIVATE_KEY]
        }
      }
    };
    ```
5. Create a directory called `ignition` and subdirectory called `modules` inside it.
    ```
    mkdir ignition
    cd ignition
    mkdir modules
    ```
6. Create a file called `HelloWorld.js` in the `ignition/modules` directory with the following content.
    ```javascript
    const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

    const HelloModule = buildModule("HelloModule", (m) => {
        const Hello = m.contract("HelloWorld", ["Hello, World!"]);

        return { Hello };
    });

    module.exports = HelloModule;
    ```
7. Deploy the contract by running the following command. On the prompt, choose yes to confirm deployment to sepolia.
    ```
    npx hardhat ignition deploy ./ignition/modules/HelloWorld.js --network sepolia
    ```
    You should see a message of the following form. The address will be different in your case.
    ```
    [dotenv@17.3.1] injecting env (4) from .env -- tip: 🛡️ auth for agents: https://vestauth.com
    ✔ Confirm deploy to network sepolia (11155111)? … yes
    Hardhat Ignition 🚀

    Deploying [ HelloModule ]

    Batch #1
      Executed HelloModule#HelloWorld

    [ HelloModule ] successfully deployed 🚀

    Deployed Addresses

    HelloModule#HelloWorld - 0xa3528D9159a19fDC28Af53b06AB8e9675D4216D8
    ```
    The contract has been deployed at the address `0xa3528D9159a19fDC28Af53b06AB8e9675D4216D8`. You can see the contract in the Sepolia block explorer at https://sepolia.etherscan.io/address/your-contract-address. Remember to fill in your contract address.