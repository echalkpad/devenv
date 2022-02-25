

[Title] AFC: S2MU004: patch for 1ohm cable & prevent 5V attach noti

[Problem] 
1. abnormal detection 1 ohm cable in fast charging case
2. 5V attach noti makes abnormal working when detach cable at the 100% battery

[Cause & Measure] 
1. 1 ohm cable : no response -> QC 
2. prevent 5V attach noti in case of cable detach






### 1. 1 ohm cable : no response -> QC 





`````````````````````````````````c

# static int s2mu004_hv_muic_handle_attach (struct s2mu004_muic_data *muic_data, const muic_afc_data_t *new_afc_data)
| switch (new_afc_data->function_num) 
| | case FUNC_TA_TO_PREPARE:
| | | schedule_delayed_work(&muic_data->afc_after_prepare, msecs_to_jiffies(60));

@ INIT_DELAYED_WORK(&muic_data->afc_after_prepare, s2mu004_muic_afc_after_prepare);


# void s2mu004_muic_afc_after_prepare(struct work_struct *work)
| # static void s2mu004_hv_muic_set_afc_after_prepare (struct s2mu004_muic_data *muic_data)
| | s2mu004_hv_muic_write_reg(muic_data->i2c, 0x5f, 0x05);
| | s2mu004_hv_muic_write_reg(muic_data->i2c, 0x4A, 0x0e);
| | schedule_delayed_work(&muic_data->afc_send_mpnack, msecs_to_jiffies(2000));
| | "2 초뒤에는 QC 로 9V 승압해야 하기 때문에"
| | "2 초뒤 cancel_delayed_work 되지 않으면 -> no response 경우 이며"
| | "afc_send_mpnack work queue 호출되어 QC prepare 설정함 mpnack "
| |--- 
| | @ INIT_DELAYED_WORK(&muic_data->afc_send_mpnack, s2mu004_muic_afc_send_mpnack);
| | # void s2mu004_muic_afc_send_mpnack(struct work_struct *work)
| | | s2mu004_hv_muic_detect_dev(muic_data, muic_data->irq_mpnack);
| | | "2초안에 cancel안되면 mpnack 번호로 detect_dev() 호출됨"
| | | "그뒤 handle_attach() 에서 case FUNC_PREPARE_TO_QC_PREPARE: 로 탐"


" cancel_delayed_work 되는 경우 두가지"
# static irqreturn_t s2mu004_muic_hv_irq(int irq, void *data)
| /* After ping , if there is response then cancle mpnack work */
| if ((irq == muic_data->irq_mrxrdy) || (irq == muic_data->irq_mpnack)) 
| | cancel_delayed_work(&muic_data->afc_send_mpnack);
| | "2초 안에 mrxrdy 인터럽트 또는 mpnack 인터럽트 오면 cancel_delayed_work"
| | "afc prepare 에서ping 날리고 2초안에 cancel 안되면 QC prepare 수행"
| s2mu004_hv_muic_detect_dev(muic_data, muic_data->afc_irq);

# bool s2mu004_muic_check_change_dev_afc_charger
| if (muic_check_dev_ta(muic_data)) 
| # bool muic_check_dev_ta(struct s2mu004_muic_data *muic_data)
| | if (vbvolt == 0 || chgtyp == 0) 
| | | s2mu004_hv_muic_reset_hvcontrol_reg(muic_data);
| | | # void s2mu004_hv_muic_reset_hvcontrol_reg(struct s2mu004_muic_data *muic_data)
| | | | cancel_delayed_work(&muic_data->afc_send_mpnack);
| | | | "reset 될때 cancel_delayed_work"

```````````````````````````````````````










### 2. Prevent 5V attach noti in case of cable detach




```c
# static int s2mu004_hv_muic_handle_attach (struct s2mu004_muic_data *muic_data, const muic_afc_data_t *new_afc_data)
| if (noti)
| | if (new_dev == ATTACHED_DEV_AFC_CHARGER_5V_MUIC)
| | | schedule_delayed_work(&muic_data->afc_cable_type_work, msecs_to_jiffies(80));
| | | "cable 디태치 시점에 AFC 5V 인식이 발생함 -> 5v noti가 충전쪽 uvlo 업데이트를 하여 LPM 100% 에서 아이콘 에러가 생김"
| | else
| | | muic_notifier_attach_attached_dev(new_dev);


@ INIT_DELAYED_WORK(&muic_data->afc_cable_type_work, s2mu004_muic_afc_cable_type_work);

# void s2mu004_muic_afc_cable_type_work(struct work_struct *work)
| ret = s2mu004_read_reg(muic_data->i2c, S2MU004_REG_AFC_STATUS, &val_vbadc);
| ret = s2mu004_read_reg(muic_data->i2c, 0X0A, &chg_sts0); // get chg in status

| chg_sts0 = chg_sts0 & CHGIN_STATUS_MASK;
| val_vbadc = val_vbadc & STATUS_VBADC_MASK;
| pr_err("%s(%d) vbadc : %d , attached_dev : %d, chg in: %02x\n " , __func__, __LINE__, val_vbadc, muic_data->attached_dev, chg_sts0);

| if(muic_data->attached_dev != ATTACHED_DEV_NONE_MUIC
| 	&& (val_vbadc != VBADC_8_7V_9_3V) |  && (!(chg_sts0 == 0x0)))
| "일반 케이블 detach인 경우에 이 조건을 타지 않음 : detach시 5V 인식되어도 noti 보내지 않음"
| | muic_notifier_attach_attached_dev(ATTACHED_DEV_AFC_CHARGER_5V_MUIC);

```








### 3. 3번째 ping 날리고 mrxrdy 인터럽트 뜨기 전에 VbADC 인터럽트 뜬 경우 호출 되는 함수의 조건이 수정됨.



```

# static irqreturn_t s2mu004_muic_hv_irq(int irq, void *data)
| if (irq == muic_data->irq_vbadc && muic_data->afc_count >= 2) "ping 3번 보낸 이후 VbADC 인터럽트 뜬 경우"
| | if (val_vbadc != VBADC_8_7V_9_3V) "vbadc 값이 9V 가 아닌경우"
| | | schedule_delayed_work(&muic_data->afc_check_vbadc, msecs_to_jiffies(100)); "100ms 뒤에 vbadc 값 다시 체크해서 9V 정상 인식"


@ INIT_DELAYED_WORK(&muic_data->afc_check_vbadc, s2mu004_muic_afc_check_vbadc);

# void s2mu004_muic_afc_check_vbadc(struct work_struct *work)
| chg_sts0 = chg_sts0 & CHGIN_STATUS_MASK;
| val_vbadc = val_vbadc & STATUS_VBADC_MASK;
| if ((muic_data->attached_dev != ATTACHED_DEV_AFC_CHARGER_9V_MUIC)
		&& (!(chg_sts0 == 0x0)) && (val_vbadc == VBADC_8_7V_9_3V)) "이 조건이 #8에서 추가됨 : 9V이고 chg 상태일때"
| | s2mu004_hv_muic_detect_dev(muic_data, muic_data->irq_vbadc); "vbadc로 다시 케이블 9V 다시 인식"
```

