cwlVersion: v1.0
class: CommandLineTool

requirements:
  - class: DockerRequirement
    dockerPull: ubuntu:xenial

inputs:

  delay:
    type: int
    inputBinding:
      position: 1
    default: 60

outputs: []

baseCommand: [sleep]