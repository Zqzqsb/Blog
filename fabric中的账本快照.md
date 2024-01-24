---
title: Fabric中的账本快照
categories:
  - 区块链
date: 2022-7-11
cover: https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/peer_channel_join_bySnapshot.png
description: 本文记录了Fabric中账本快照的相关实验记录。
tags:
  - Fabric
  - 区块链
---

## fabric 中的账本快照

## 介绍

账本快照是 Fabric v2.3 引入的两个功能之一。快照为我们提供了一种将新节点加入 Fabric 网络的替代方式。在本文中，我们将重点介绍账本快照，并演示其工作原理。

## 结构总览

- 以 peer channel join 的方式从创世块加入通道。 这是默认的加入方式，新 peer 将维护 channel 中的所有区块。

  ![peer_channel_join](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/peer_channel_join.png)

- 以 snapshot 方式加入通道。 新 peer 不再维护 snapshot 之前的区块

  ![join_by_snapshot](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/peer_channel_join_bySnapshot.png)

## 实验

### 1.启动测试网络

```shell
cd test-network
./network.sh up createChannel -ca
```

![start_testNetwork](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/start_test_network.png)

可以看到现在块高度是 3。 下为状态图示。

![blocksize_3](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/blocksize_3.png)

### 2.部署和查询链码

```shell
./network.sh deployCC -ccn mycc -ccp ../chaincode/sacc -ccl go
```

```shell
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls true --cafile $ORDERER_CA -C mychannel -n mycc --peerAddresses localhost:7051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses localhost:9051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"Args":["set","name","Peter"]}'
```

![blocksize_7](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/blocksize_7.png)

操作后链高变为 7。

### 3.准备新的节点(org1.peer1)

- 加密材料 同 org1.peer0

  ```shell
  export FABRIC_CA_CLIENT_HOME=${PWD}/organizations/peerOrganizations/org1.example.com/
  fabric-ca-client register --caname ca-org1 --id.name peer1 --id.secret peer1pw --id.type peer --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  mkdir -p organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com
  fabric-ca-client enroll -u https://peer1:peer1pw@localhost:7054 --caname ca-org1 -M ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/msp --csr.hosts peer1.org1.example.com --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/msp/config.yaml ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/msp/config.yaml
  fabric-ca-client enroll -u https://peer1:peer1pw@localhost:7054 --caname ca-org1 -M ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls --enrollment.profile tls --csr.hosts peer1.org1.example.com --csr.hosts localhost --tls.certfiles ${PWD}/organizations/fabric-ca/org1/tls-cert.pem
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls/tlscacerts/* ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls/ca.crt
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls/signcerts/* ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls/server.crt
  cp ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls/keystore/* ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls/server.key
  ```

- compose file

  ```yaml
  # Copyright IBM Corp. All Rights Reserved.
  #
  # SPDX-License-Identifier: Apache-2.0
  #

  version: "2"

  volumes:
    peer1.org1.example.com:

  networks:
    test:

  services:
    peer1.org1.example.com:
      container_name: peer1.org1.example.com
      image: hyperledger/fabric-peer:$IMAGE_TAG
      environment:
        #Generic peer variables
        - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock
        # the following setting starts chaincode containers on the same
        # bridge network as the peers
        # https://docs.docker.com/compose/networking/
        - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=${COMPOSE_PROJECT_NAME}_test
        - FABRIC_LOGGING_SPEC=INFO
        #- FABRIC_LOGGING_SPEC=DEBUG
        - CORE_PEER_TLS_ENABLED=true
        - CORE_PEER_PROFILE_ENABLED=true
        - CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt
        - CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key
        - CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt
        # Peer specific variabes
        - CORE_PEER_ID=peer1.org1.example.com
        - CORE_PEER_ADDRESS=peer1.org1.example.com:8051
        - CORE_PEER_LISTENADDRESS=0.0.0.0:8051
        - CORE_PEER_CHAINCODEADDRESS=peer1.org1.example.com:8052
        - CORE_PEER_CHAINCODELISTENADDRESS=0.0.0.0:8052
        - CORE_PEER_GOSSIP_BOOTSTRAP=peer1.org1.example.com:8051
        - CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer1.org1.example.com:8051
        - CORE_PEER_LOCALMSPID=Org1MSP
      volumes:
        - /var/run/:/host/var/run/
        - ../organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/msp:/etc/hyperledger/fabric/msp
        - ../organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls:/etc/hyperledger/fabric/tls
        - peer1.org1.example.com:/var/hyperledger/production
      working_dir: /opt/gopath/src/github.com/hyperledger/fabric/peer
      command: peer node start
      ports:
        - 8051:8051
      networks:
        - test
  ```

- 启动容器

  ```shell
  docker-compose -f docker/docker-compose-peer1org1.yaml up -d
  ```

- 更换 peer 环境(在下一步的某些操作中需要)

  ```shell
  CORE_PEER_ADDRESS=localhost:8051 peer channel list
  ```

### 4.使用 snapshot 加入通道

- 通过 peer0.org1 创建 snapshot

  ```shell
  peer snapshot submitrequest -c mychannel -b 0 --peerAddress localhost:7051 --tlsRootCertFile ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
  ```

- 这个快照位于 peer0.org1 的容器中 我们把它从容器中取出

  ```shell
  docker cp peer0.org1.example.com:/var/hyperledger/production/snapshots/completed/mychannel/6/ snapshot
  ```

- 使用快照加入通道

  ```shell
  CORE_PEER_ADDRESS=localhost:8051 peer channel joinbysnapshot --snapshotpath /opt/gopath/src/github.com/hyperledger/fabric/peer/snapshot/
  ```

- 切换 peer 并查看装

  ```shell
  CORE_PEER_ADDRESS=localhost:8051 peer channel list
  CORE_PEER_ADDRESS=localhost:8051 peer channel getinfo -c mychannel
  ```

  ![code](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/join_by_snapshot_code.png)

  ![structure](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/join_by_snapshot_structure.png)

### 测试链码

- 安装链码

  ```shell
  CORE_PEER_ADDRESS=localhost:8051 peer lifecycle chaincode install mycc.tar.gz
  ```

- 查询链码

  ```shell
  CORE_PEER_ADDRESS=localhost:8051 peer chaincode query -C mychannel -n mycc -c '{"Args":["get","name"]}'
  ```

  ![query_chaincode](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/query_chaincode.png)

​ 结果正常。

- 测试背书

  ```shell
  peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls true --cafile $ORDERER_CA -C mychannel -n mycc --peerAddresses localhost:8051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer1.org1.example.com/tls/ca.crt --peerAddresses localhost:9051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"Args":["set","name","Mary"]}'
  ```

​ 结果正常。

![query_res](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/query_result.png)

- 进行新的查询(会创建新块)

  ```shell
  peer chaincode query -C mychannel -n mycc -c '{"Args":["get","name"]}'
  ```

      ![image-20230809162744543](/Users/zq/Library/Application Support/typora-user-images/image-20230809162744543.png)

​ 结果正常。

- 链状状态

![chain_status](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/chain_status.png)

### 同步块

- 尝试同步快照之前的节点

  ![fetch_previousr](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/fetch_previous.png)

  不可行。

- 只能同步快照之后的节点(7 开始)

  ![fetch_after_snapshot](https://alicloud-pic.oss-cn-shanghai.aliyuncs.com/BlogImg/Other/fabric_%E8%B4%A6%E6%9C%AC%E5%BF%AB%E7%85%A7/fetch_after_snapshot.png)

### 关闭网络

- 关闭网络

  ```shell
  ./network.sh down
  ```

- 清理容器

  ```shell
  docker volume prune
  ```

## 总结

本文介绍和试验了 fabric 中账本快照的用法。
