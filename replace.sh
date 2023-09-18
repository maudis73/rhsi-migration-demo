skupper service create backend 6000
skupper service bind backend deployment/backend
kill $(lsof -t -i :6000)
skupper gateway forward backend 6000

