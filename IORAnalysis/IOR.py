import numpy as n


class IOR():
    '''
    Calculates IOR Rating for Defined Yacht.
    Default values are for Indulgence.

    Calculates IOR rating from certificate values.
    Provides access to all calculated parameters from the IOR
    certificate.
    The class performs all calculations required to achieve a
    correct SC and CGF for a sloop rig such as Indulgence. It
    does not contain any calculations regarding a mizzen or other
    unusual sails, or any calculations based on hull measurements.

    Parameters
    ----------
    cert : :obj:`dict`
        Dictionary containing certificate values for the yacht.
    ballastChange : :obj:`list`
        List containing [Ballast Amount, Distance  Moved].
        Direction follows standard ship conventions, with
        upwards being positive.

    Attributes
    ----------
    Certificate Values : :obj:`floats`
        All certificate values are available as attributes

    Rating : :obj:`float`
        Rating in it's official form, rounded to 1 d.p.

    ballastChange : :obj:`list`
        List containing difference from basis vessel ballast
        position in the format [Ballast Amount, Distance  Moved].
        Direction follows standard ship conventions, with
        upwards being positive.

    actualCGF : :obj:`float`
        Calculated CGF value. Differs from certificate CGF only if
        less than the minimum value of 0.9860.

    '''

    def __init__(s, cert={}, ballastChange=[0, 0]):
        base_cert = {
            'L': 30.8953, 'B': 11.42, 'D': 3.8691,
            'DC': 0.0293, 'FC': -0.0682, 'I': 43.232,
            'J': 12.4, 'LPG': 18, 'LPIS': 0, 'FSP': 0.16,
            'IG': 42.9, 'SPL': 12.31, 'SL': 40.5,
            'SMW': 21.9, 'P': 48.53, 'E': 17.27,
            'BAL': 0.5, 'BD': 0.87, 'BAD': 5.56,
            'HB': 0.67, 'CGF': 0.968, 'EPF': 0.9641,
            'MAF': 1, 'DLF': 1.0032, 'SMF': 1, 'LRP': 1,
            'CBF': 1,
        }

        for k in base_cert:
            try:
                setattr(s, k, cert[k])
            except KeyError:
                setattr(s, k, base_cert[k])

        s.ballastChange = ballastChange

        s.Calc()

    def updateCert(s, changes: list):
        '''
        Updates certificate values stored in attributes

        Parameters
        ----------
        changes : :obj:`list`
            * :obj:`dict`
                Dictionary containing changes to certificate values for
                the yacht.
            * :obj:`list`
                List containing [Ballast Amount, Distance  Moved].
                Direction follows standard ship conventions, with
                upwards being positive.

        '''
        for k in changes[0]:
            setattr(s, k, changes[0][k])
        try:
            s.ballastChange = changes[1]
        except IndexError:
            pass
        s.Calc()

    def __sailCalcs(s) -> float:
        '''
        Calculates **SC** based on certificate sail parameters

        Performs all relevant calculations for a standard sloop rigged yacht
        to calculate the corrected sail area **SC**


        Returns
        -------
        :obj:`float`
            **SC**, rated sail area.

        '''

        s.EC = s.E + (s.BAL - 0.5)

        s.PC = s.P
        if(s.BAD > 0.05 * s.P + 4):
            s.PC = s.PC + (s.BAD - (0.05 * s.P + 4))
        if(s.P + s.BAD < 0.96 * s.I):
            s.PC = s.PC + (0.96 * s.I - (s.P + s.BAD))
        if(s.BD > 0.05 * s.E):
            s.PC = s.PC + (s.BD - 0.05 * s.E)
        if(s.HB > n.max([0.04 * s.E, 0.5])):
            s.PC = s.PC + (s.HB - n.max([0.04 * s.E, 0.5])) * s.P / s.E

        s.JC = n.max([s.J, s.SPL, s.SMW / 1.8])

        s.LP = n.max([s.LPG + s.FSP, 1.5 * s.JC, s.LPIS])
        s.LL = 0.95 * n.sqrt(n.power(s.I, 2) + n.power(s.JC, 2))

        s.SPIN = 1.01 * s.JC * n.max([s.LL, s.SL])

        s.IC = s.I
        if(s.SL > s.LL):
            s.IC = s.IC + (2 * s.SL - s.LL)

        s.RSAM = 0.35 * (s.PC * s.EC)
        if(0.2 * s.EC * (s.PC - s.E * 2) > 0):
            s.RSAM = s.RSAM + 0.2 * s.EC * (s.PC - s.E * 2)

        s.RSAF = 0.5 * s.IC * s.JC * (1 + 1.1 * ((s.LP - s.JC) / s.LP))
        if (0.125 * s.JC * (s.IC - 2 * s.JC) > 0):
            s.RSAF = s.RSAF + (0.125 * s.JC * (s.IC - 2 * s.JC))

        s.SATC = 0.1 * (s.RSAF - 1.43 * s.RSAM)
        s.RSAT = s.SATC + s.RSAF + s.RSAM
        s.SC = n.sqrt(n.max([s.RSAT, s.SPIN]))
        return s.SC

    def __CGFCalc(s, ballastChange: list) -> float:
        '''
        Calculates **CGF**.

        Calculates **CGF**, sets s.actualCGF to the calculated value.
        If **CGF** < 0.968 (the minimum in the rule), returns 0.968.


        Parameters
        ----------
        ballastChange : :obj:`list`
            List containing [Ballast Amount, Distance  Moved].
            Direction follows standard ship conventions, with
            upwards being positive.


        Returns
        -------
        :obj:`float`
            **CGF**, centre of gravity factor.
        '''

        CGF = (2.2 / ((34562.05963 / (
            871.13 - ballastChange[0] * ballastChange[1])) - 5.1)) + 0.8925
        s.actualCGF = CGF
        if (CGF >= 0.9680):
            return CGF
        else:
            return 0.968

    def Calc(s):
        '''
        Calculates final rated length.

        Runs calculations for CGF and SC, then calculates
        MR, R, Rating and TCF
        '''

        s.CGF = s.__CGFCalc(s.ballastChange)
        s.SC = s.__sailCalcs()

        s.MR = ((0.13 * s.L * s.SC) / n.sqrt(s.B * s.D) +
                0.25 * s.L + 0.2 * s.SC + s.DC + s.FC) * s.DLF
        s.R = s.MR * s.EPF * s.CGF * s.MAF * s.SMF * s.LRP * s.CBF

        s.Rating = round(s.R, 1)
        s.TCF = (0.2424 * n.sqrt(s.Rating)) / (1 + 0.0567 * n.sqrt(s.Rating))

    def ReqRMChange(s, reqRating: float) -> float:
        '''
        Calculates the RM change required to acheive a certain rating.

        Parameters
        ----------
        reqRating : :obj:`float`
            The desired rating for which RM change should be calculated, to 1 d.p.

        Returns
        -------
        :obj:`float`
            The required change in righting moment to achieve reqRating,
            given in lb feet.
        '''

        reqCGF = reqRating / (s.MR * s.EPF * s.MAF * s.SMF * s.LRP * s.CBF)
        reqRMChange = 871.13 - \
            (1 / (((1 / ((reqCGF - 0.8925) / 2.2)) + 5.1) / 34562.0593))
        return reqRMChange
