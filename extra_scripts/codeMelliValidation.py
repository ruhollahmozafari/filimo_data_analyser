class codeMelliChecker():
    def checker(codeMelli: str):
        # check that code melli must be digits
        if not codeMelli.isnumeric():
            return False
        # check that code melli must be in 10 digits
        if len(codeMelli) != 10:
            return False

        cityCode = codeMelli[:3]
        controlNumber = int(codeMelli[9])

        sum = 0
        place = 10
        for i in codeMelli[:9]:
            sum += int(i) * place
            place -= 1

        mod = sum % 11
        if mod == 0 and controlNumber == 0:
            return True

        elif mod == 1 and controlNumber == 1:
            return True

        elif (11 - mod) == controlNumber:
            return True

        return False
