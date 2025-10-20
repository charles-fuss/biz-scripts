[Convert]::ToBase64String([IO.File]::ReadAllBytes("config.yaml")) | Set-Content -NoNewline "config.yaml.b64"
