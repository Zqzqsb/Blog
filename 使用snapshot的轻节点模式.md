# 使用snapshot的轻节点模式

## 创建TestNetWork

+ 包含一个channel(channel1) 该channel包含org1-peer和org2-peer。

  ![image-20230808154650302](/Users/zq/Library/Application Support/typora-user-images/image-20230808154650302.png)

+ 在网络中注册链码

  ![image-20230808154934780](/Users/zq/Library/Application Support/typora-user-images/image-20230808154934780.png)

+ 设置交互所需的环境变量

  ```shell
  export PATH=${PWD}/../bin:$PATH
  export FABRIC_CFG_PATH=$PWD/../config/
  ```

+  查看区块链信息

  ```shell
  peer channel getinfo -c mychannel
  ```

  ![image-20230808155818127](/Users/zq/Library/Application Support/typora-user-images/image-20230808155818127.png)

​		 目前的块高度为8

## 创建账本快照

+ 切换环境并创建快照

  ```shell
  export CORE_PEER_TLS_ENABLED=true
  export CORE_PEER_LOCALMSPID="Org2MSP"
  export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
  export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
  export CORE_PEER_ADDRESS=localhost:9051
  ```
  ```shell
  peer snapshot submitrequest -c mychannel -b 0 --peerAddress localhost:9051 --tlsRootCertFile /Users/zq/WorkSpace/Projects/fabric-samples/test-network/organizations/peerOrganizations/org2.example.com/tlsca/tlsca.org2.example.com-cert.pem
  ```

  ![image-20230808161333668](/Users/zq/Library/Application Support/typora-user-images/image-20230808161333668.png) R

+ 查看pending

  ```shell
  peer snapshot listpending -c mychannel --peerAddress localhost:9051 --tlsRootCertFile /Users/zq/WorkSpace/Projects/fabric-samples/test-network/organizations/peerOrganizations/org2.example.com/tlsca/tlsca.org2.example.com-cert.pem
  Successfully got pending snapshot requests: [8]
  ```

+ 在文件系统中定位快照

  