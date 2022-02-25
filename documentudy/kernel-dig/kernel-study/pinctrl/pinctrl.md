
"drivers/pinctrl/"

### For examples

#### 1.

"drivers/i2c/busses/i2c-s3c2410.c"

```dts
i2c@13870000 {                                                                           
	...
        s2mu005@3d {                                                                     
		...
                pinctrl-names = "default";                                               
                pinctrl-0 = <&if_irq &if_pmic_rstb>;  
		...
	}
```

```c
# static int s3c24xx_i2c_probe(struct platform_device *pdev)
| i2c->pctrl = devm_pinctrl_get_select_default(i2c->dev);

```
> It is selected by "default" pin when probing!!!





#### 2.

```dts
i2c@13840000 {
	...
        touchscreen@49 {                         
		...
                pinctrl-names = "on_state", "off_state"; 
                pinctrl-0 = <&attn_irq &tsp_1p8_en>; 
                pinctrl-1 = <&attn_input>; 
		...
	}

```

```c
# int mms_power_control(struct mms_ts_info *info, int enable)
| struct pinctrl_state *pinctrl_state;
| if (enable)
| 	pinctrl_state = pinctrl_lookup_state(info->pinctrl, "on_state");
| else
| 	pinctrl_state = pinctrl_lookup_state(info->pinctrl, "off_state");
| ret = pinctrl_select_state(info->pinctrl, pinctrl_state);

```





#### 3. gen panel

```dts
panel {
        compatible = "marvell,mmp-dsi-panel";
        pinctrl-names = "default", "enable", "disable";
        pinctrl-0 = <&lcd_esd_pmx &lcd_rst_pmx_idle>;
        pinctrl-1 = <&lcd_rst_pmx_idle>;
        pinctrl-2 = <&lcd_rst_pmx_sleep>;
	...
}
```

```c
"drivers/video/backlight/gen_panel/gen_panel.c"
# static int gen_panel_parse_dt_pinctrl(
                struct platform_device *pdev, struct lcd *lcd)
| struct pinctrl *pinctrl;
| struct pinctrl_state *pinctrl_state;
| pinctrl = devm_pinctrl_get(&pdev->dev);
| pinctrl_state = pinctrl_lookup_state(lcd->pinctrl, "enable");
| lcd->pin_enable = pinctrl_state;
| pinctrl_state = pinctrl_lookup_state(lcd->pinctrl, "disable");
| lcd->pin_disable = pinctrl_state;
```

```c
"drivers/video/backlight/gen_panel/gen_panel.c"
# static int gen_panel_set_pin_state(struct lcd *lcd, int on)
| pinctrl_state = on ? lcd->pin_enable : lcd->pin_disable;
| ret = pinctrl_select_state(lcd->pinctrl, pinctrl_state);

```


```c
```


TODO
pinctrl  gpio setting check!!

