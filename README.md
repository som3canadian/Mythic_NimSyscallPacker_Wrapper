# Mythic_NimSyscallPacker_Wrapper

## Description

Mythic C2 wrapper for NimSyscallPacker. This is similar to the [scarescrow_wrapper](https://github.com/MythicAgents/scarecrow_wrapper) but for NimSyscallPacker made by S3cur3Th1sSh1t (sponsors only). So yeah, to use this wrapper you need to be a [sponsor of S3cur3Th1sSh1t](https://github.com/sponsors/S3cur3Th1sSh1t).

![Screenshot1](./assets/screenshot1.jpg)

![Screenshot2](./assets/screenshot2.jpg)

![Screenshot4](./assets/screenshot4.jpg)

## Requirements

- Having Mythic installed and running
- Having an agent installed and working (ex: apollo)
- You are being able to generate a payload (ex: apollo csharp payload), run it on a target machine and receive a callback.
- Being a [sponsor of S3cur3Th1sSh1t](https://github.com/sponsors/S3cur3Th1sSh1t)

## Usage

### Install and setup NimSyscallPacker wrapper

First step is to install the NimSyscallPacker wrapper in your Mythic instance.

```bash
git clone https://github.com/som3canadian/Mythic_NimSyscallPacker_Wrapper.git nimsyscallpacker_wrapper
cd nimsyscallpacker_wrapper/Payload_Type/nimsyscallpacker_wrapper/agent_code
#
# git clone NimSyscallPacker from S3cur3Th1sSh1t private repo
# p.s: You just need to clone the repo in this folder. Docker will take care of the rest
git clone git@github.com:S3cur3Th1sSh1t...
#
# go in the path where you can you run mythic-cli
cd /path/to/mythic
./mythic-cli install folder /path/to/repo/agents/nimsyscallpacker_wrapper
```

Since this is not an official Mythic agent, you need to modify the agent config to support the new wrapper. You can do this by modifying the `builder.py` file in the agent's folder. For example, for the apollo agent, you can modify the `builder.py` file located in `<mythic installation folder>/InstalledServices/apollo/apollo/mythic/agent_functions/builder.py`. Restart after modification.

note for merlin: `/path/to/Mythic/InstalledServices/merlin/container/payload/build/build.go`

![screenshot3](./assets/screenshot3.jpg)

At this point you should be able to see the packer in the Mythic UI and create a payload using the new wrapper. You need to create a basic payload first (like apollo or any other agents that can be use with the wrapper).

## Todo

- [ ] Integrate more options (build parameters) in the wrapper
- [ ] Manage more formats (pwsh, xll, etc)
- [ ] Better documentation

## Credits

- [S3cur3Th1sSh1t](https://github.com/S3cur3Th1sSh1t)
- [its-a-feature](https://github.com/its-a-feature)
