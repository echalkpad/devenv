extcon 코드 공부 내용.    
  
target : core prime ve lte  
  
sm5504_muic_cable_handler 호출  
idx = sm5504_detect_cable(info);  
extcon_set_cable_state(info->edev, cable_names[idx], attached);  
> raw_notifier_call_chain(&edev->nh, old_state, edev);  
> 따라가면 결국 위의 함수 호출하여 notify call 호출.  
		  
  
  
어떤 notifier가 호출되는지?  
  
- extcon_sec_probe(struct platform_device *pdev)   
  
- extcon_register_notifier(extsec_info->phy_edev,  
			&extsec_info->extsec_nb);  
  
> &extsec_info->extsec_nb 에 등록된 notifier_call 호출  
  
- extsec_info->extsec_nb.notifier_call = extsec_notifier;  
  
- static int extsec_notifier(struct notifier_block *nb,  
			   unsigned long state, void *phy_edev)  
{  
	struct extcon_sec *extsec_info =  
		container_of(nb, struct extcon_sec, extsec_nb);  
  
	schedule_work(&extsec_info->wq);  
  
	return NOTIFY_OK;  
}  
  
  
- INIT_WORK(&extsec_info->wq, extsec_work_cb);  
  
- static void extsec_work_cb(struct work_struct *wq)  
> 결국 이 함수가 호출됨.    
  
  
