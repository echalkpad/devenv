[Title] AFC: S2MU004: Stability patch for detection 1 ohm cable with AFC TA

[Problem] 
If there are fail to rise 9V in AFC TA, It needs to more retried ping afc master ping and setting QC D+D- voltage 

[Cause & Measure]
Increase retry count of afc master ping to x20 and QC to x3







### 1. afc ping x20


# static void s2mu004_hv_muic_set_afc_after_prepare (struct s2mu004_muic_data *muic_data)
| muic_data->retry_cnt = 0;
| s2mu004_mpnack_irq_mask(muic_data, 0);
| s2mu004_hv_muic_write_reg(muic_data->i2c, 0x5f, 0x05); "tx 버퍼 채우는것? -> 아님"
| "참고: s2mu004_muic_prepare_afc_charger() tx 버퍼는 여기서 채움 (muic에서DCP인식후 바로 call)"
| s2mu004_hv_muic_write_reg(muic_data->i2c, 0x4A, 0x0e); "ping tx data start 핑 전송"
| schedule_delayed_work(&muic_data->afc_send_mpnack, msecs_to_jiffies(2000));
| schedule_delayed_work(&muic_data->afc_control_ping_retry, msecs_to_jiffies(50));
| "afc prepare 시 mrxrdy 받을 때 까지 ping 전송을 20회 반복 함."

@ INIT_DELAYED_WORK(&muic_data->afc_control_ping_retry, s2mu004_muic_afc_control_ping_retry);

# static void s2mu004_muic_afc_control_ping_retry(struct work_struct *work)
| if (muic_data->retry_cnt <  RETRY_PING_CNT) "20회까지 반복 #define RETRY_PING_CNT 20"
| | muic_data->retry_cnt++;
| | s2mu004_hv_muic_write_reg(muic_data->i2c, 0x4A, 0x0e); "ping tx data start 핑 전송"
| | schedule_delayed_work(&muic_data->afc_control_ping_retry, msecs_to_jiffies(50));
| | "50ms 뒤에 s2mu004_muic_afc_control_ping_retry 함수 다시시작"
| else
| | muic_data->retry_cnt = 0;
| | s2mu004_mpnack_irq_mask(muic_data, 1); /* enable mpnack irq */
| | "이후 QC 모드로 변경하기 위한 사전작업"
| | s2mu004_hv_muic_write_reg(muic_data->i2c, 0x4A, 0x0e);


" cancel_delayed_work 되는 경우"
# static irqreturn_t s2mu004_muic_hv_irq(int irq, void *data)
| if ((irq == muic_data->irq_mrxrdy) || (irq == muic_data->irq_mpnack))
| | cancel_delayed_work(&muic_data->afc_send_mpnack);
| | "afc prepare 에서ping 날리고 2초안에 cancel 안되면 QC prepare 수행"
| | cancel_delayed_work(&muic_data->afc_control_ping_retry);
| | "retry 20회 도중 mrxrdy 인터럽트 받으면 ping retry 하던걸 중지함 "








### 2. QC setting x3

# static int s2mu004_hv_muic_handle_attach
| "QC prepare 동작"
| case FUNC_PREPARE_TO_QC_PREPARE:
| | muic_data->afc_count = 0;
| | muic_data->qc_prepare = 1;
| | s2mu004_hv_muic_write_reg(muic_data->i2c, 0x5f, 0x01);"D+D- QC 레벨 설정인듯?"
| | s2mu004_hv_muic_write_reg(muic_data->i2c, 0x49, 0xbd);
| | schedule_delayed_work(&muic_data->afc_qc_retry, msecs_to_jiffies(50));
 
@ INIT_DELAYED_WORK(&muic_data->afc_qc_retry, s2mu004_muic_afc_qc_retry);


# void s2mu004_muic_afc_qc_retry(struct work_struct *work)
| if (muic_data->retry_qc_cnt < RETRY_QC_CNT) "#define RETRY_QC_CNT 3"
| | muic_data->retry_qc_cnt++;
| | s2mu004_hv_muic_write_reg(muic_data->i2c, 0x49, 0x00);
| | s2mu004_hv_muic_write_reg(muic_data->i2c, 0x49, 0xbd);
| | schedule_delayed_work(&muic_data->afc_qc_retry, msecs_to_jiffies(50));
| | "50ms 뒤에 QC retry"
| else
| | muic_data->retry_qc_cnt = 0;
| | muic_data->qc_prepare = 0;
   
   
"QC retry cancel 되는 경우"
# static irqreturn_t s2mu004_muic_hv_irq(int irq, void *data)
| if ((irq == muic_data->irq_vbadc) && (muic_data->qc_prepare == 1))
| | muic_data->qc_prepare = 0;
| | cancel_delayed_work(&muic_data->afc_qc_retry);
