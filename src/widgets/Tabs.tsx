import React from 'react';

export interface ITab {
  id: string;
  label: string;
  badge?: number | string;
}

interface TabsProps {
  tabs: ITab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  className?: string;
  activeClassName?: string;
  inactiveClassName?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
  className = 'jp-WWCExtension-synthesis-tabs',
  activeClassName = 'jp-WWCExtension-tab-active',
  inactiveClassName = 'jp-WWCExtension-tab'
}) => {
  return (
    <div className={className}>
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={activeTab === tab.id ? activeClassName : inactiveClassName}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
          {tab.badge !== undefined && ` (${tab.badge})`}
        </button>
      ))}
    </div>
  );
};
