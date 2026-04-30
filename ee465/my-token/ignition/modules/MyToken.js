const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

const MyTokenModule = buildModule("MyTokenModule", (m) => {
    const MyToken = m.contract("PSToken");
    return { MyToken };
});

module.exports = MyTokenModule;