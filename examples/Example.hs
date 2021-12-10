module Example where

import Clash.Prelude

counter :: Unsigned 3 -> Bool -> (Unsigned 3, Unsigned 1)
counter state enable = (state', resize (state `shiftR` 2))
    where
        state' = if enable
            then state + 1
            else state

counterA :: forall dom . 
    HiddenClockResetEnable dom =>
        Signal dom (Bool) -> Signal dom (Unsigned 1)
counterA enable = resize <$> state'
    where
        state = register 0 state' :: Signal dom (Unsigned 3)
        state' = (+1) <$> state

counterM :: HiddenClockResetEnable dom =>
    Signal dom (Bool) -> Signal dom (Unsigned 1)
counterM = mealy counter 0

{-# ANN topEntity
  (Synthesize
    { t_name = "counter"
    , t_inputs = [ PortName "clk", PortName "rst", PortName "en", PortName "enable" ]
    , t_output = PortName "sum_lsb"
    }) #-}
topEntity
    :: Clock System
    -> Reset System
    -> Enable System
    -> Signal System (Bool)
    -> Signal System (Unsigned 1)
topEntity = exposeClockResetEnable counterM